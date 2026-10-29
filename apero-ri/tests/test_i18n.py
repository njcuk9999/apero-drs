#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Request-local language selection and safe ARI translations."""
from pathlib import Path
from string import Formatter
import sys

import pytest
from flask import Flask, render_template_string
from markupsafe import Markup

from apero_ri.core import i18n


@pytest.fixture()
def language_app() -> Flask:
    """Return an isolated app with only the language route and context."""
    app = Flask(__name__)
    app.add_url_rule('/set_language/<lang>', 'set_language',
                     i18n.set_language_view)
    app.context_processor(i18n.context)
    return app


@pytest.mark.parametrize('header, expected', [
    ('fr-CA,fr;q=0.9,en;q=0.8', 'fr'),
    ('es-MX,es;q=0.9', 'es'),
    ('de', 'en'),
    ('fr;q=0,es;q=0.8', 'es'),
])
def test_browser_language(language_app: Flask, header: str,
                          expected: str) -> None:
    """Select a supported language using browser quality preferences."""
    with language_app.test_request_context(
        headers={'Accept-Language': header}
    ):
        assert i18n.get_language() == expected


def test_switch_cookie_overrides_browser(language_app: Flask) -> None:
    """Persist the selected language without changing browser preferences."""
    client = language_app.test_client()
    response = client.get('/set_language/es?next=/login?v=8')
    assert response.headers['Location'] == '/login?v=8'
    cookie = response.headers['Set-Cookie']
    assert 'ari_lang=es' in cookie
    assert 'HttpOnly' in cookie
    assert 'SameSite=Lax' in cookie
    with language_app.test_request_context(
        headers={'Cookie': 'ari_lang=es', 'Accept-Language': 'fr'}
    ):
        assert i18n.get_language() == 'es'
    response = client.get('/set_language/de')
    assert 'Set-Cookie' not in response.headers


@pytest.mark.parametrize('target', [
    '//evil.example', '/\\evil.example', 'javascript:alert(1)', '',
])
def test_switch_rejects_unsafe_redirect(language_app: Flask,
                                        target: str) -> None:
    """Never redirect to a scheme-relative or backslash-based host."""
    response = language_app.test_client().get(
        '/set_language/fr', query_string={'next': target}
    )
    assert response.headers['Location'] == '/'


def test_translation_and_escaping(language_app: Flask) -> None:
    """Escape translated text and untrusted interpolation values."""
    with language_app.test_request_context(
        headers={'Accept-Language': 'fr'}
    ):
        assert i18n.translate('Login') == 'Connexion'
        assert i18n.translate('Unknown text') == 'Unknown text'
        template = "{{ _('Hello {name}', name=name) }}"
        output = render_template_string(template, name='<script>')
        assert output == 'Hello &lt;script&gt;'
        output = render_template_string(template, name=Markup('<code>x</code>'))
        assert output == 'Hello <code>x</code>'
        assert render_template_string("{{ _('{missing}') }}") == '{missing}'


def test_table_placeholders() -> None:
    """Keep every English placeholder intact in both translations."""
    table = i18n.load_table(force=True)
    assert table
    formatter = Formatter()
    for english, translations in table.items():
        fields = {part[1] for part in formatter.parse(english) if part[1]}
        assert set(translations) == {'FR', 'ES'}
        for translation in translations.values():
            translated = {
                part[1] for part in formatter.parse(translation) if part[1]
            }
            assert translated == fields, english


def test_templates_compile(language_app: Flask) -> None:
    """Compile all templates with the newly registered language filter."""
    language_app.jinja_env.filters['tl'] = i18n.translate
    root = Path(i18n.__file__).parent.parent / 'templates'
    for path in root.rglob('*.html'):
        language_app.jinja_env.parse(path.read_text(encoding='utf-8'))


def test_application_language_integration(monkeypatch, tmp_path) -> None:
    """Render the real home page using browser and cookie selection."""
    from apero_ri.application.application import ARIApp

    monkeypatch.setattr(sys, 'argv', ['ari'])
    monkeypatch.setenv('ARI_DATA_DIR', str(tmp_path))
    app = ARIApp()
    app.config.update(TESTING=True, RATELIMIT_ENABLED=False)
    client = app.test_client()
    response = client.get('/', headers={'Accept-Language': 'fr'})
    assert response.status_code == 200
    assert '<html lang="fr"' in response.text
    assert 'Interface de réduction' in response.text
    response = client.get('/set_language/es?next=/', follow_redirects=True)
    assert response.status_code == 200
    assert '<html lang="es"' in response.text
    assert 'Interfaz de reducción' in response.text
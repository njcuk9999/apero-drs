#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Permission-aware search index for documentation and site pages."""

from html.parser import HTMLParser
from typing import Any

from flask import jsonify, request, session
from jinja2 import nodes

from apero_ri.core import auth, docs, permissions


class _PageText(HTMLParser):
    """Extract visible static text while excluding scripts and styles."""

    def __init__(self) -> None:
        """Initialize parser state."""
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """Track non-content elements.

        :param tag: HTML tag.
        :param attrs: Element attributes.
        :return: None.
        """
        if tag in {'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        """Leave non-content elements.

        :param tag: HTML tag.
        :return: None.
        """
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        """Collect visible text.

        :param data: HTML text.
        :return: None.
        """
        if not self.hidden:
            self.parts.append(data)


def _template_text(app: Any, template: str, seen: set) -> str:
    """Read visible static text, including shared template fragments.

    :param app: ARI template environment owner.
    :param template: Template name.
    :param seen: Template names visited in this traversal.
    :return: Searchable static page text.
    """
    if template in seen:
        return ''
    seen.add(template)
    parser = _PageText()
    content = []
    try:
        source = app.jinja_env.loader.get_source(app.jinja_env, template)[0]
        tree = app.jinja_env.parse(source)
        for fragment in tree.find_all(nodes.TemplateData):
            parser.feed(fragment.data)
        content.extend(parser.parts)
        for include in tree.find_all(nodes.Include):
            if isinstance(include.template, nodes.Const):
                name = include.template.value
                if isinstance(name, str):
                    content.append(_template_text(app, name, seen))
    except Exception:
        pass
    return ' '.join(content)


def search_index(app: Any) -> Any:
    """Return searchable text for permitted pages and documentation.

    :param app: ARI application with page definitions and template loader.
    :return: JSON index containing label, URL, keywords, and category.
    """
    user = auth.get_effective_user(session)
    group_args = [user['groups'], app.ari_groups] if user else []
    perms = (permissions.resolve_user_permissions(*group_args)
             if user else auth.get_public_permissions())
    if not permissions.has_view_permission('view.home', perms):
        return jsonify(items=[]), 403
    version = request.args.get('v') or docs.get_default_version()
    items = []
    if permissions.has_view_permission('view.doc', perms):
        for record in docs.get_search_index(version):
            items.append(dict(record, category='Documentation'))
    if request.args.get('scope', 'site') == 'docs':
        return jsonify(items=items)
    for page_id, definition in app.ari_pages.items():
        required = definition.get('view-permission', '')
        if not permissions.has_view_permission(required, perms):
            continue
        if '{' in page_id or definition.get('external-url'):
            continue
        if page_id in {'home.login', 'home.logout'}:
            continue
        if page_id.startswith('home.user_portal') and not user:
            continue
        template = permissions.page_id_to_template(page_id, app.ari_pages)
        label = str(definition.get('label', page_id))
        url = permissions.page_id_to_url(page_id)
        content = _template_text(app, template, set())
        keywords = ' '.join([label, url, content]).lower()
        items.append(dict(label=label, url=url, keywords=keywords,
                          category='Site'))
    return jsonify(items=items)
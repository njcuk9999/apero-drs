"""Documentation view helper functions for ARIApp."""

from apero_ri.core import auth, docs
from apero_ri.core.permissions import (
    has_view_permission,
    resolve_user_permissions,
)
from flask import flash, redirect, render_template, request, session, url_for


def _pretty_label(page_ref: str) -> str:
    """Build a readable page label from a doc ref."""
    ref = str(page_ref or '').strip('/').split('/')
    token = ref[-1] if ref else 'Documentation'
    token = token.replace('_', ' ').replace('-', ' ').strip()
    if not token:
        token = 'Documentation'
    return ' '.join(part.capitalize() for part in token.split())


def _doc_edit_allowed(perms, page_ref: str) -> bool:
    """Check edit permissions with full-path and leaf fallback."""
    if 'edit.doc' in perms:
        return True
    if any(str(perm).startswith('edit.doc.') for perm in perms):
        return True

    ref = str(page_ref or '').strip('/').replace('/', '.')
    leaf = str(page_ref or '').strip('/').split('/')[-1]
    for perm_name in (f'edit.doc.{ref}', f'edit.doc.{leaf}'):
        if perm_name in perms:
            return True
    return False


def _short_ref_from_norm(norm_ref: str) -> str:
    """Return docs short ref from normalized ``home/docs/...`` ref."""
    normalized = docs.normalize_doc_ref(norm_ref)
    if normalized == 'home/docs':
        return ''
    return normalized[len('home/docs/'):]


def _cards_to_sidebar_items(cards: list, raw_ref: str, depth: int) -> list:
    """Convert docs cards into sidebar items at one visual depth."""
    current_norm = docs.normalize_doc_ref(raw_ref)
    items = []
    for card in cards:
        url = str(card.get('url') or '').strip()
        if not url.startswith('/docs'):
            continue
        short_ref = ''
        if url.startswith('/docs/'):
            short_ref = url[len('/docs/'):]
        card_norm = docs.normalize_doc_ref(short_ref)
        item_id = 'home.docs'
        if short_ref:
            item_id = 'home.docs.' + short_ref.replace('/', '.')

        item = dict()
        item['id'] = item_id
        item['label'] = str(card.get('label') or '').strip()
        item['icon'] = str(
            card.get('icon') or 'fa-solid fa-file-lines'
        ).strip()
        item['url'] = url
        item['depth'] = depth
        item['kind'] = 'file'
        item['has_children'] = False
        item['pinned'] = False
        item['disabled'] = False
        item['active'] = (card_norm == current_norm)
        items.append(item)
    return items


def _resolve_docs_level(raw_ref: str, version: str):
    """Resolve cards and branch-expanded sidebar for docs pages."""
    cards, current_ver, _ = docs.get_doc_cards(raw_ref, version)
    exists = docs.doc_exists(raw_ref, version)

    nav_version = current_ver or version
    root_cards, nav_version, _ = docs.get_doc_cards('', nav_version)
    sidebar_items = _cards_to_sidebar_items(root_cards, raw_ref, depth=0)

    short_ref = _short_ref_from_norm(docs.normalize_doc_ref(raw_ref))
    tokens = [tok for tok in short_ref.split('/') if tok]
    for idx in range(len(tokens)):
        branch_short = '/'.join(tokens[: idx + 1])
        branch_cards, nav_version, _ = docs.get_doc_cards(
            branch_short,
            nav_version,
        )
        if not branch_cards:
            break
        branch_items = _cards_to_sidebar_items(
            branch_cards,
            raw_ref,
            depth=idx + 1,
        )
        sidebar_items.extend(branch_items)

    if exists and not cards:
        normalized = docs.normalize_doc_ref(raw_ref)
        parts = normalized.split('/')
        if len(parts) > 2:
            parent_norm = '/'.join(parts[:-1])
        else:
            parent_norm = 'home/docs'
        parent_short = _short_ref_from_norm(parent_norm)
        cards, current_ver, _ = docs.get_doc_cards(parent_short, version)

    return cards, current_ver, sidebar_items, exists


def doc_dynamic_view(app, page_ref: str = ''):
    """Render a docs page or docs directory listing from path refs."""
    user_info = auth.get_effective_user(session)
    if user_info:
        perms = resolve_user_permissions(user_info['groups'], app.ari_groups)
    else:
        perms = auth.get_public_permissions()

    if not has_view_permission('view.doc', perms):
        flash('You do not have permission to view this page.', 'warning')
        return redirect(url_for('login'))

    raw_ref = str(page_ref or '').strip('/')
    normalized = docs.normalize_doc_ref(raw_ref)
    short_ref = normalized[len('home/docs/'):]
    root_def = app.ari_pages.get('home.docs', {})
    page_id = 'home.docs'
    page_label = (
        root_def.get('label', 'Documentation')
        if not short_ref else _pretty_label(short_ref)
    )
    page_icon = root_def.get('icon', 'fa-brands fa-readme')

    version = request.args.get('v') or docs.get_default_version()
    view_mode = str(request.args.get('view', 'cards') or 'cards').strip()
    if view_mode not in {'cards', 'list'}:
        view_mode = 'cards'

    cards, current_ver, docs_sidebar, exists = _resolve_docs_level(
        raw_ref,
        version,
    )

    query_parts = []
    if current_ver:
        query_parts.append(f'v={current_ver}')
    if view_mode == 'list':
        query_parts.append('view=list')

    query_suffix = ''
    if query_parts:
        query_suffix = '?' + '&'.join(query_parts)

    self_url = '/docs'
    if short_ref:
        self_url = '/docs/' + short_ref

    context = {
        'page_id': page_id,
        'page_label': page_label,
        'page_icon': page_icon,
        'doc_versions': docs.get_versions(),
        'current_version': current_ver,
        'doc_ref': short_ref,
        'docs_sidebar_tree': docs_sidebar,
        'view_mode': view_mode,
        'doc_query_suffix': query_suffix,
        'doc_self_url': self_url,
    }
    context.update(app._build_sidebar_context(page_id, perms, user_info))
    base_sidebar = list(context.get('sidebar_tree', []))
    pinned = [item for item in base_sidebar if item.get('pinned', False)]
    context['sidebar_tree'] = pinned + docs_sidebar

    if exists:
        raw, html, _ = docs.get_doc_content(raw_ref, current_ver)
        modified = docs.get_doc_last_modified(raw_ref, current_ver)
        context.update(
            {
                'doc_html': html,
                'doc_raw': raw,
                'doc_ref': short_ref,
                'doc_last_modified': modified,
                'can_edit': _doc_edit_allowed(perms, short_ref),
            }
        )
        return render_template('docs/doc_page.html', **context)

    context['cards'] = cards
    return render_template('docs/index.html', **context)


def doc_edit_view(app, page_ref: str):
    """Show the split-view markdown editor for a doc page."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        flash("You must be logged in to edit documentation.", "warning")
        return redirect(url_for("login"))

    perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    clean_ref = str(page_ref or '').strip('/')
    if clean_ref:
        view_url = url_for('doc_dynamic_view', page_ref=clean_ref)
    else:
        view_url = url_for('home_docs')

    if not _doc_edit_allowed(perms, clean_ref):
        flash("You do not have permission to edit this page.", "warning")
        return redirect(view_url)

    root_def = app.ari_pages.get('home.docs', {})
    page_label = _pretty_label(clean_ref) if clean_ref else root_def.get(
        'label', 'Documentation'
    )
    page_icon = root_def.get('icon', 'fa-brands fa-readme')

    version = request.args.get("v") or docs.get_default_version()
    raw, _html, current_ver = docs.get_doc_content(clean_ref, version)

    version_name = current_ver or "New"
    for ver in docs.get_versions():
        if ver["id"] == current_ver:
            version_name = ver["name"]
            break

    context = {
        "page_id": "home.docs",
        "page_label": page_label,
        "page_icon": page_icon,
        "doc_ref": clean_ref,
        "doc_raw": raw,
        "version_id": current_ver,
        "version_name": version_name,
        "view_url": view_url,
        'docs_sidebar_tree': _resolve_docs_level(clean_ref, current_ver)[2],
    }
    context.update(app._build_sidebar_context('home.docs', perms, user_info))
    docs_sidebar = list(context.get('docs_sidebar_tree', []))
    base_sidebar = list(context.get('sidebar_tree', []))
    pinned = [item for item in base_sidebar if item.get('pinned', False)]
    context['sidebar_tree'] = pinned + docs_sidebar
    context["doc_versions"] = docs.get_versions()
    context["current_version"] = current_ver

    return render_template("docs/doc_editor.html", **context)

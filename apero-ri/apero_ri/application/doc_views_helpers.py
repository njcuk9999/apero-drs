"""Documentation view helper functions for ARIApp."""

from apero_ri.core import auth, docs
from apero_ri.core.permissions import (
    page_id_to_endpoint,
    resolve_user_permissions,
)
from flask import flash, redirect, render_template, request, session, url_for


def doc_edit_view(app, page_ref: str):
    """Show the split-view markdown editor for a doc page."""
    user_info = auth.get_effective_user(session)
    if not user_info:
        flash("You must be logged in to edit documentation.", "warning")
        return redirect(url_for("login"))

    perms = resolve_user_permissions(user_info["groups"], app.ari_groups)
    page_id = f"home.docs.{page_ref}"
    edit_perm = f"edit.doc.{page_ref}"
    if edit_perm not in perms:
        flash("You do not have permission to edit this page.", "warning")
        return redirect(url_for(f"home_docs_{page_ref}"))

    page_def = app.ari_pages.get(page_id)
    if not page_def:
        flash("Page not found.", "danger")
        return redirect(url_for("home_docs"))

    version = request.args.get("v") or docs.get_default_version()
    raw, _html, current_ver = docs.get_doc_content(page_id, version)

    version_name = current_ver or "New"
    for ver in docs.get_versions():
        if ver["id"] == current_ver:
            version_name = ver["name"]
            break

    context = {
        "page_id": page_id,
        "page_label": page_def.get("label", ""),
        "page_icon": page_def.get("icon", ""),
        "page_endpoint": page_id_to_endpoint(page_id),
        "doc_ref": page_ref,
        "doc_raw": raw,
        "version_id": current_ver,
        "version_name": version_name,
    }
    context.update(app._build_sidebar_context(page_id, perms, user_info))
    context["doc_versions"] = docs.get_versions()
    context["current_version"] = current_ver

    return render_template("docs/doc_editor.html", **context)

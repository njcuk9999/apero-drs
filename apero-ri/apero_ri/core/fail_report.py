#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI - Processing-log fail-report helpers.

Pure-logic helpers (no Flask) for the "Generate Fail Report" feature on the
processing-logs PID page:

  - Error-line extraction and grouping (templating similar errors together).
  - On-disk storage of generated PDF reports plus a public share-token store
    so a report can be downloaded/shared via an unguessable, expiring URL.
"""
from __future__ import annotations

import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apero_ri.core import secret_store as ss


__NAME__ = "apero_ri.core.fail_report"

# APERO log-level markers.
ERROR_MARKER = "-!!|"
WARN_MARKER = "-@!|"

# Tolerant matchers (allow optional internal whitespace around the marker).
_ERROR_MARKER_RE = re.compile(r"-\s*!!\s*\|")
_WARN_MARKER_RE = re.compile(r"-\s*@!\s*\|")

# Where generated PDF reports live on disk.
ARI_DIR = Path.home() / ".ari"
REPORTS_DIRNAME = "reports"

# How long a share/download token stays valid.
REPORT_EXPIRY_HOURS = 24

# Token format (uuid4).
_TOKEN_RE = re.compile(r"^[0-9a-f-]{36}$")

# Guards writes to the token store.
_TOKEN_LOCK = threading.Lock()


# =============================================================================
# Error grouping
# =============================================================================
def _strip_log_prefix(line: str) -> str:
    """Strip the APERO log prefix from an error-marked line.

    Real APERO log lines look like::

        HH:MM:SS.sss-!!|RECIPE_NAME[pid]|actual message text

    There are two ``|`` characters: the one embedded in ``-!!|`` and a
    second one separating the recipe/PID label from the message body.
    Both are stripped so callers see only the message.

    :param line: one raw log line.
    :return: the message text, or the stripped line when no marker is found.
    """
    for matcher in (_ERROR_MARKER_RE, _WARN_MARKER_RE):
        match = matcher.search(line)
        if match:
            rest = line[match.end():]
            # Strip the optional "RECIPE_NAME[pid]|" label that follows.
            pipe = rest.find("|")
            if pipe >= 0:
                rest = rest[pipe + 1:]
            return rest.strip()
    return line.strip()


# Substitutions applied (in order) to turn a concrete error message into a
# stable "signature". Each replaces a variable part with a placeholder so that
# two messages differing only in paths/numbers/ids collapse to one group.
_NORMALIZE_RULES: List[Tuple[re.Pattern, str]] = [
    # Windows + POSIX absolute/relative file paths.
    (re.compile(r"(/[^\s'\"]+)+/?"), "<PATH>"),
    (re.compile(r"[A-Za-z]:\\[^\s'\"]+"), "<PATH>"),
    # Quoted strings (single or double).
    (re.compile(r"'[^']*'"), "<STR>"),
    (re.compile(r'"[^"]*"'), "<STR>"),
    # Bracket-enclosed identifiers: object names, class refs, target pairs
    # e.g. [BPS_CS_22881M0003_GL699], [GJ643_GJ643], [LblException].
    # Must start with a letter so pure-numeric PIDs like [01052] fall through
    # to the number rule below.
    (re.compile(r"\[[A-Za-z][^\[\]\n]{0,120}\]"), "[<ID>]"),
    # Hex / uuid-like blobs.
    (re.compile(r"\b[0-9a-fA-F]{8,}\b"), "<HEX>"),
    # ISO-ish dates and times.
    (re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?"), "<DATE>"),
    (re.compile(r"\d{2}:\d{2}:\d{2}(?:\.\d+)?"), "<TIME>"),
    # Floats and integers (incl. scientific notation, signed).
    (re.compile(r"[-+]?\d+\.\d+(?:[eE][-+]?\d+)?"), "<NUM>"),
    (re.compile(r"\b\d+\b"), "<NUM>"),
]


def _is_code_context(message: str) -> bool:
    """Return True when a stripped log message looks like a traceback/code line.

    These lines are excluded from block signatures so two blocks that share
    the same top-level error message but have different stack frames still
    group together.
    """
    s = message.strip()
    if not s:
        return True
    return bool(
        s.startswith("Traceback (most recent call last)")
        or s.startswith('File "')
        or re.match(r"^\s{4,}", message)   # deeply-indented code line
        or re.match(r"^\^+\s*$", s)        # ^^^^ caret pointer line
        or re.match(r"^\s*\.\.\.\s*$", s)  # ... ellipsis
    )


def _first_content_line(block: List[str]) -> str:
    """Return the first non-empty, non-traceback message from a block."""
    for line in block:
        msg = _strip_log_prefix(str(line))
        if msg and not _is_code_context(msg):
            return msg
    return ""


def _template_and_vars(message: str) -> Tuple[str, List[str]]:
    """Apply normalization rules with numbered placeholders.

    Unlike :func:`normalize_error_message` (which uses generic tags), this
    numbers every captured variable so callers can reconstruct which value
    occupied which slot in each occurrence, enabling a "variables" breakdown.

    :param message: already-prefix-stripped error message.
    :return: ``(template_string, [captured_value_1, captured_value_2, ...])``.
    """
    captured: List[str] = []
    result = message.strip()
    for pattern, _ in _NORMALIZE_RULES:
        parts: List[str] = []
        pos = 0
        for m in pattern.finditer(result):
            parts.append(result[pos:m.start()])
            captured.append(m.group(0))
            # Prefix the index with a letter inside null-byte delimiters so
            # no \b word boundary forms before the digit — preventing the
            # integer normalization rule from matching the index itself.
            parts.append("\x00V%d\x00" % len(captured))
            pos = m.end()
        parts.append(result[pos:])
        result = "".join(parts)
    # Convert null-byte placeholders to {{N}} after all rules have run.
    result = re.sub(r"\x00V(\d+)\x00", r"{{\1}}", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result, captured


def normalize_error_message(message: str) -> str:
    """Reduce a concrete error message to a stable grouping signature.

    Variable parts (paths, numbers, quoted strings, hex blobs, dates) are
    replaced with placeholders so messages that differ only in those parts
    map to the same signature.

    :param message: error message text (already prefix-stripped).
    :return: normalized signature string.
    """
    sig = message.strip()
    for pattern, repl in _NORMALIZE_RULES:
        sig = pattern.sub(repl, sig)
    # Collapse whitespace so spacing differences do not split groups.
    sig = re.sub(r"\s+", " ", sig).strip()
    return sig


def extract_error_lines(log_text: str) -> List[str]:
    """Return the error-marked (``-!!|``) lines from one log file's text.

    :param log_text: full text content of one APERO log file.
    :return: list of raw lines that contain the error marker.
    """
    out: List[str] = []
    for line in (log_text or "").splitlines():
        if _ERROR_MARKER_RE.search(line):
            out.append(line.rstrip())
    return out


def extract_error_blocks(log_text: str) -> List[List[str]]:
    """Extract *contiguous blocks* of error-marked lines from a log file.

    A block starts when a line containing ``-!!|`` is encountered and ends
    when the next line does not contain ``-!!|``.  Each block is a distinct
    error event; the same error repeated in separate blocks will be grouped
    together by :func:`group_error_blocks`.

    :param log_text: full text content of one APERO log file.
    :return: list of blocks, where each block is a list of raw lines.
    """
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in (log_text or "").splitlines():
        if _ERROR_MARKER_RE.search(line):
            current.append(line.rstrip())
        else:
            if current:
                blocks.append(current)
                current = []
    if current:
        blocks.append(current)
    return blocks


def _normalize_block(lines: List[str]) -> str:
    """Produce a stable signature for one error block.

    Traceback / code-context lines are skipped so two blocks that carry the
    same error message but different stack frames still collapse to the same
    group.  Adjacent duplicate normalised lines are also deduplicated (APERO
    sometimes repeats the final exception message at the end of the block).

    :param lines: raw ``-!!|`` lines that make up one error block.
    :return: normalised multi-line signature string.
    """
    sig_lines = []
    for line in lines:
        msg = _strip_log_prefix(str(line))
        if not msg or _is_code_context(msg):
            continue
        sig_lines.append(normalize_error_message(msg))
    # Remove adjacent duplicates (repeated exception line at block end).
    deduped: List[str] = []
    for ln in sig_lines:
        if not deduped or deduped[-1] != ln:
            deduped.append(ln)
    return "\n".join(deduped)


def _representative_block(blocks: List[List[str]]) -> List[str]:
    """Pick a representative block from a group of similar blocks.

    Prefers the median-length block (avoids the shortest, which may be
    truncated, and the longest, which may be unusually verbose).

    :param blocks: list of raw line-lists for one error group.
    :return: the chosen representative block.
    """
    if not blocks:
        return []
    sorted_by_len = sorted(blocks, key=lambda b: sum(len(l) for l in b))
    return sorted_by_len[len(sorted_by_len) // 2]


def group_error_blocks(
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Group similar error blocks and extract a variable-breakdown template.

    Blocks that differ only in variable parts (paths, object names, numbers,
    bracket-enclosed identifiers) are collapsed into one group. For each
    group the first non-traceback message line is templated — variable parts
    become ``{{1}}``, ``{{2}}``, … — so the output shows:

    * the abstract error shape (template),
    * how many times it occurred and in how many recipes,
    * which distinct values each ``{{N}}`` placeholder took.

    :param items: list of dicts with keys ``'label'`` (recipe/log name) and
                  ``'error_blocks'`` (list of blocks from
                  :func:`extract_error_blocks`).
    :return: list of group dicts sorted by descending count, each::

        {
            'signature':   <normalised block signature>,
            'template':    <first content line with {{N}} placeholders>,
            'var_unique':  {'1': [val, ...], '2': [val, ...], ...},
            'count':       <number of block occurrences>,
            'recipe_count': <number of distinct recipes affected>,
            'block_lines': <representative raw block (list of strings)>,
            'message':     <first stripped content line of representative block>,
            'recipes':     [<distinct recipe labels>],
            'sample_blocks': [<up to 2 raw sample blocks>],
        }
    """
    groups: Dict[str, Dict[str, Any]] = dict()
    for item in items or []:
        label = str(item.get("label", "") or "")
        for block in item.get("error_blocks", []) or []:
            if not block:
                continue
            signature = _normalize_block(block)
            if not signature:
                continue
            grp = groups.get(signature)
            if grp is None:
                grp = dict(
                    signature=signature,
                    count=0,
                    blocks=[],
                    recipes=[],
                    template="",
                    var_unique={},  # str(N) -> [unique values]
                )
                groups[signature] = grp
            grp["count"] += 1
            grp["blocks"].append(list(block))
            if label and label not in grp["recipes"]:
                grp["recipes"].append(label)
            # Extract template + variable values from first content line.
            first_line = _first_content_line(block)
            if first_line:
                tmpl, vals = _template_and_vars(first_line)
                if not grp["template"]:
                    grp["template"] = tmpl
                for i, val in enumerate(vals):
                    key = str(i + 1)
                    bucket = grp["var_unique"].setdefault(key, [])
                    if val not in bucket:
                        bucket.append(val)

    out: List[Dict[str, Any]] = []
    for grp in groups.values():
        rep_block = _representative_block(grp["blocks"])
        message = _first_content_line(rep_block)
        out.append(dict(
            signature=grp["signature"],
            template=grp["template"],
            var_unique=grp["var_unique"],
            count=int(grp["count"]),
            recipe_count=len(grp["recipes"]),
            block_lines=rep_block,
            message=message,
            recipes=list(grp["recipes"]),
            sample_blocks=grp["blocks"][:2],
        ))
    out.sort(key=lambda g: (-g["count"], g["message"]))
    return out


def build_display_template(
    template: str,
    var_unique: Dict[str, List[str]],
) -> Tuple[str, Dict[str, List[str]]]:
    """Produce a clean display template and the truly-varying variable map.

    Constant variables (only one unique value across all occurrences) are
    substituted back into the template so they don't clutter the display.
    Varying variables are renumbered ``{{1}}``, ``{{2}}``, … in order of
    their first appearance so the caller sees a compact, sequential labelling.

    :param template: raw template string with ``{{N}}`` placeholders.
    :param var_unique: ``{str(N): [unique_values]}`` from
                       :func:`group_error_blocks`.
    :return: ``(display_template, varying_var_unique)`` where
             ``varying_var_unique`` uses the new sequential keys.
    """
    constant: Dict[str, str] = {}
    varying_keys: List[str] = []
    for k, vals in (var_unique or {}).items():
        if not vals:
            continue
        if len(vals) == 1:
            constant[k] = vals[0]
        else:
            varying_keys.append(k)
    # Sort varying keys by original number so renumbering is deterministic.
    varying_keys.sort(key=lambda x: int(x) if x.isdigit() else 0)
    renumber: Dict[str, str] = {k: str(i + 1)
                                 for i, k in enumerate(varying_keys)}

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        k = m.group(1)
        if k in constant:
            return constant[k]
        if k in renumber:
            return "{{%s}}" % renumber[k]
        return m.group(0)

    display = re.sub(r"\{\{(\d+)\}\}", _replace, template)

    new_var_unique: Dict[str, List[str]] = {
        renumber[k]: list(var_unique[k])
        for k in varying_keys
    }
    return display, new_var_unique


# Keep the old name as an alias for any callers that pass error_lines
# (single-line items) — wraps each line as a one-line block.
def group_errors(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compatibility wrapper: convert ``error_lines`` items to block form."""
    block_items = []
    for item in items or []:
        block_items.append(dict(
            label=item.get("label", ""),
            error_blocks=[[ln] for ln in (item.get("error_lines") or []) if ln],
        ))
    return group_error_blocks(block_items)


# =============================================================================
# Time / formatting helpers
# =============================================================================
def format_duration(seconds: Optional[float]) -> str:
    """Render a second count as ``HHh MMm SSs`` (omitting leading zero units).

    :param seconds: duration in seconds (None/<0 -> 'n/a').
    :return: human-readable duration string.
    """
    if seconds is None:
        return "n/a"
    try:
        total = int(round(float(seconds)))
    except (TypeError, ValueError):
        return "n/a"
    if total < 0:
        return "n/a"
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes or hours:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


# =============================================================================
# Report storage + share tokens
# =============================================================================
def set_ari_dir(path: Path) -> None:
    """Re-point the module-level ARI dir (mirrors basket_funcs.set_ari_dir)."""
    global ARI_DIR
    ARI_DIR = Path(path)


def _reports_dir() -> Path:
    """Return (creating) the directory that stores generated PDF reports."""
    env_dir = os.environ.get("ARI_DIR")
    base = Path(env_dir).expanduser() if env_dir else ARI_DIR
    path = base / REPORTS_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def _report_tokens_path() -> Path:
    """Return the managed secret file holding report share tokens."""
    env_ari_dir = (
        Path(os.environ.get("ARI_DIR", str(ARI_DIR))).expanduser().resolve()
    )
    return ss.resolve_secret_file(
        "report_tokens.json",
        legacy_paths=[env_ari_dir / "report_tokens.json"],
    )


def _load_report_tokens() -> Dict[str, Any]:
    path = _report_tokens_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_report_tokens(tokens: Dict[str, Any]) -> None:
    path = _report_tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(tokens, fh, indent=2)
    ss.protect_path(path, 0o600)


def _report_index_path() -> Path:
    """Return the path to the report-results index file."""
    env_dir = os.environ.get("ARI_DIR")
    base = Path(env_dir).expanduser() if env_dir else ARI_DIR
    return base / REPORTS_DIRNAME / "report_index.json"


def _load_report_index() -> Dict[str, Any]:
    path = _report_index_path()
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_report_index(index: Dict[str, Any]) -> None:
    path = _report_index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)


def _report_cache_key(profile_id: str, pid: str) -> str:
    return "%s:%s" % (str(profile_id or "").strip(),
                      str(pid or "").strip())


def update_report_cache(
    profile_id: str, pid: str, token: str, filename: str
) -> None:
    """Record a newly generated report in the report index.

    :param profile_id: APERO profile identifier.
    :param pid: Processing PID / group name.
    :param token: The share/download token for this report.
    :param filename: Suggested download filename.
    """
    with _TOKEN_LOCK:
        index = _load_report_index()
        key = _report_cache_key(profile_id, pid)
        index[key] = dict(
            token=token,
            filename=filename,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        _save_report_index(index)


def get_report_cache_status(
    profile_id: str, pid: str
) -> Optional[Dict[str, Any]]:
    """Return cached report info for a profile+pid, or None if absent/expired.

    The entry always returns even when the PDF token has expired (> 24 h), so
    callers can show "last generated N hours ago" and decide whether to
    re-generate.

    :return: dict with ``token``, ``filename``, ``generated_at`` (ISO),
             ``age_hours`` (float), ``token_valid`` (bool), or None when no
             entry exists.
    """
    index = _load_report_index()
    key = _report_cache_key(profile_id, pid)
    entry = index.get(key)
    if not entry:
        return None
    generated_str = str(entry.get("generated_at", "") or "")
    age_hours: float = -1.0
    if generated_str:
        try:
            generated_at = datetime.fromisoformat(generated_str)
            if generated_at.tzinfo is None:
                generated_at = generated_at.replace(tzinfo=timezone.utc)
            delta = datetime.now(timezone.utc) - generated_at
            age_hours = delta.total_seconds() / 3600.0
        except Exception:
            pass
    # The token itself is valid (PDF file still on disk) if < 24 h.
    token_valid = 0.0 <= age_hours < float(REPORT_EXPIRY_HOURS)
    # Also check the PDF file actually exists.
    token = str(entry.get("token", "") or "")
    if token_valid and token:
        resolved = resolve_report_token(token)
        token_valid = resolved is not None
    return dict(
        token=token,
        filename=str(entry.get("filename", "fail_report.pdf")),
        generated_at=generated_str,
        age_hours=round(age_hours, 2),
        token_valid=token_valid,
    )


def store_report_pdf(pdf_bytes: bytes, meta: Dict[str, Any]) -> str:
    """Persist a generated PDF and return a public share/download token.

    :param pdf_bytes: the rendered PDF content.
    :param meta: metadata to store alongside (profile_id, pid, filename...).
    :return: the share token (uuid4 string).
    """
    token = str(uuid.uuid4())
    report_dir = _reports_dir() / token
    report_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = report_dir / "fail_report.pdf"
    with open(pdf_path, "wb") as fh:
        fh.write(pdf_bytes)

    record = dict(meta or {})
    record["created_at"] = datetime.now(timezone.utc).isoformat()
    record["pdf_path"] = str(pdf_path)
    with open(report_dir / "meta.json", "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)

    with _TOKEN_LOCK:
        tokens = _load_report_tokens()
        tokens[token] = dict(
            created_at=record["created_at"],
            pdf_path=str(pdf_path),
            filename=str(meta.get("filename", "fail_report.pdf")),
        )
        _save_report_tokens(tokens)
    return token


def resolve_report_token(token: str) -> Optional[Dict[str, Any]]:
    """Return ``{'pdf_path', 'filename'}`` for a valid, non-expired token.

    :param token: the share token.
    :return: dict with the resolved PDF path + download filename, or None.
    """
    if not token or not _TOKEN_RE.match(str(token)):
        return None
    tokens = _load_report_tokens()
    entry = tokens.get(str(token))
    if not entry:
        return None
    created_str = str(entry.get("created_at", "") or "")
    if created_str:
        try:
            created_at = datetime.fromisoformat(created_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            cutoff = datetime.now(timezone.utc) - timedelta(
                hours=REPORT_EXPIRY_HOURS
            )
            if created_at < cutoff:
                return None
        except Exception:
            pass
    pdf_path = Path(str(entry.get("pdf_path", "") or ""))
    if not pdf_path.is_file():
        return None
    return dict(
        pdf_path=str(pdf_path),
        filename=str(entry.get("filename", "fail_report.pdf")),
    )

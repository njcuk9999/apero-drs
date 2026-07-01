"""Query helper utilities extracted from ARIApp."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Tuple

import yaml


def build_safe_select_query(
    table_access: Dict[str, Dict[str, Any]],
    query_spec: Dict[str, Any],
    run_ids: Iterable[str],
) -> Tuple[str, Dict[str, Any], List[str]]:
    """Build a safe parameterized SELECT from a structured query spec."""
    allowed_ops = frozenset(
        {"=", "!=", "<", ">", "<=", ">=", "LIKE", "NOT LIKE"}
    )
    allowed_in_ops = frozenset({"IN", "NOT IN"})
    allowed_null_ops = frozenset({"IS NULL", "IS NOT NULL"})
    allowed_join_types = frozenset({"INNER", "LEFT", "RIGHT"})
    allowed_sort_dirs = frozenset({"ASC", "DESC"})

    def q_id(name: str) -> str:
        if not re.match(r"^[A-Za-z0-9_]+$", name):
            raise ValueError(f"Invalid identifier: {name!r}")
        return f"`{name}`"

    tables_spec = query_spec.get("tables", [])
    joins_spec = query_spec.get("joins", [])
    filters_spec = query_spec.get("filters", [])
    order_by_spec = query_spec.get("order_by")
    limit = int(query_spec.get("limit", 500))
    # limit=0 means "no limit" (return all rows)
    if limit != 0:
        limit = min(max(1, limit), 2000)

    if not tables_spec:
        raise ValueError("No tables specified.")

    table_names: Dict[str, str] = {}
    table_cols: Dict[str, set] = {}
    select_parts: List[str] = []
    col_labels: List[str] = []

    for tspec in tables_spec:
        label = str(tspec.get("label", "")).strip().upper()
        if label not in table_access:
            raise ValueError(f"Table {label!r} is not accessible.")
        allowed = table_access[label]["columns"]
        tname = table_access[label]["table_name"]
        if not re.match(r"^[A-Za-z0-9_.]+$", tname):
            raise ValueError(f"Invalid table name: {tname!r}")
        table_names[label] = tname
        table_cols[label] = set(allowed)

        cols = tspec.get("columns") or list(allowed)
        for col in cols:
            col = str(col).strip()
            if col not in table_cols[label]:
                raise ValueError(
                    f"Column {col!r} is not accessible for {label}."
                )
            alias = f"{label}__{col}"
            select_parts.append(f"`_t_{label}`.{q_id(col)} AS {q_id(alias)}")
            col_labels.append(alias)

    basket_key_cols = ["KW_RUN_ID", "BLOCK_KIND", "OBS_DIR", "FILENAME"]
    if "FINDEX" in table_cols:
        for bk_col in basket_key_cols:
            bk_alias = f"FINDEX__{bk_col}"
            if bk_alias not in col_labels and bk_col in table_cols["FINDEX"]:
                select_parts.append(
                    f"`_t_FINDEX`.{q_id(bk_col)} AS {q_id(bk_alias)}"
                )

    if not select_parts:
        raise ValueError("No columns selected.")

    first_label = str(tables_spec[0].get("label", "")).strip().upper()
    first_tname = table_names[first_label]
    from_clause = f"`{first_tname}` AS `_t_{first_label}`"

    join_clauses: List[str] = []
    for jspec in joins_spec:
        left = str(jspec.get("left_label", "")).strip().upper()
        right = str(jspec.get("right_label", "")).strip().upper()
        left_col = str(jspec.get("left_col", "")).strip()
        right_col = str(jspec.get("right_col", "")).strip()
        jtype = str(jspec.get("type", "LEFT")).strip().upper()

        if left not in table_names or right not in table_names:
            raise ValueError("Join references an inaccessible table.")
        if jtype not in allowed_join_types:
            raise ValueError(f"Invalid join type: {jtype!r}")
        if left_col not in table_cols[left]:
            raise ValueError(
                f"Join column {left_col!r} not accessible for {left}."
            )
        if right_col not in table_cols[right]:
            raise ValueError(
                f"Join column {right_col!r} not accessible for {right}."
            )

        right_tname = table_names[right]
        join_clauses.append(
            f"{jtype} JOIN `{right_tname}` AS `_t_{right}` "
            f"ON `_t_{left}`.{q_id(left_col)} = `_t_{right}`.{q_id(right_col)}"
        )

    where_parts: List[str] = []
    params: Dict[str, Any] = {}
    param_idx = 0

    if "FINDEX" in table_names:
        run_ids_sorted = sorted(run_ids)
        if not run_ids_sorted:
            return "SELECT 1 WHERE 1=0", {}, []
        params["_run_ids"] = run_ids_sorted
        where_parts.append("`_t_FINDEX`.`KW_RUN_ID` IN :_run_ids")

    for fspec in filters_spec:
        tlabel = str(fspec.get("table_label", "")).strip().upper()
        col = str(fspec.get("column", "")).strip()
        op_raw = str(fspec.get("op", "")).strip().upper()

        if tlabel not in table_names:
            raise ValueError(
                f"Filter references an inaccessible table: {tlabel!r}"
            )
        if col not in table_cols[tlabel]:
            raise ValueError(
                f"Filter column {col!r} not accessible for {tlabel}."
            )

        col_ref = f"`_t_{tlabel}`.{q_id(col)}"

        if op_raw in allowed_null_ops:
            where_parts.append(f"{col_ref} {op_raw}")
        elif op_raw in allowed_in_ops:
            raw_values = fspec.get("values") or []
            if not isinstance(raw_values, list):
                raw_values = [raw_values]
            values = [str(v) for v in raw_values if str(v).strip()]
            if not values:
                raise ValueError(
                    f"IN filter on {col!r} requires at least one value."
                )
            pname = f"p{param_idx}"
            param_idx += 1
            where_parts.append(f"{col_ref} {op_raw} :{pname}")
            params[pname] = values
        elif op_raw in allowed_ops:
            pname = f"p{param_idx}"
            param_idx += 1
            where_parts.append(f"{col_ref} {op_raw} :{pname}")
            params[pname] = fspec.get("value", "")
        else:
            raise ValueError(f"Invalid filter operator: {op_raw!r}")

    order_clause = ""
    if order_by_spec and isinstance(order_by_spec, dict):
        ob_label = str(order_by_spec.get("table_label", "")).strip().upper()
        ob_col = str(order_by_spec.get("column", "")).strip()
        ob_dir = str(order_by_spec.get("direction", "ASC")).strip().upper()
        if ob_label in table_names and ob_col:
            if ob_col not in table_cols[ob_label]:
                raise ValueError(
                    f"Order column {ob_col!r} not accessible for {ob_label}."
                )
            if ob_dir not in allowed_sort_dirs:
                ob_dir = "ASC"
            order_clause = f"ORDER BY `_t_{ob_label}`.{q_id(ob_col)} {ob_dir}"

    sql = f'SELECT {", ".join(select_parts)}\nFROM {from_clause}'
    for jc in join_clauses:
        sql += f"\n{jc}"
    if where_parts:
        sql += f'\nWHERE {" AND ".join(where_parts)}'
    if order_clause:
        sql += f"\n{order_clause}"
    if limit != 0:
        sql += f"\nLIMIT {limit}"

    return sql, params, col_labels


def build_safe_count_query(
    table_access: Dict[str, Dict[str, Any]],
    query_spec: Dict[str, Any],
    run_ids: Iterable[str],
) -> Tuple[str, Dict[str, Any]]:
    """Build a SELECT COUNT(*) version of the query (no ORDER BY, no LIMIT)."""
    allowed_ops = frozenset(
        {"=", "!=", "<", ">", "<=", ">=", "LIKE", "NOT LIKE"}
    )
    allowed_in_ops = frozenset({"IN", "NOT IN"})
    allowed_null_ops = frozenset({"IS NULL", "IS NOT NULL"})
    allowed_join_types = frozenset({"INNER", "LEFT", "RIGHT"})

    def q_id(name: str) -> str:
        if not re.match(r"^[A-Za-z0-9_]+$", name):
            raise ValueError(f"Invalid identifier: {name!r}")
        return f"`{name}`"

    tables_spec = query_spec.get("tables", [])
    joins_spec = query_spec.get("joins", [])
    filters_spec = query_spec.get("filters", [])

    if not tables_spec:
        raise ValueError("No tables specified.")

    table_names: Dict[str, str] = {}
    table_cols: Dict[str, set] = {}

    for tspec in tables_spec:
        label = str(tspec.get("label", "")).strip().upper()
        if label not in table_access:
            raise ValueError(f"Table {label!r} is not accessible.")
        allowed = table_access[label]["columns"]
        tname = table_access[label]["table_name"]
        if not re.match(r"^[A-Za-z0-9_.]+$", tname):
            raise ValueError(f"Invalid table name: {tname!r}")
        table_names[label] = tname
        table_cols[label] = set(allowed)

    first_label = str(tables_spec[0].get("label", "")).strip().upper()
    first_tname = table_names[first_label]
    from_clause = f"`{first_tname}` AS `_t_{first_label}`"

    join_clauses: List[str] = []
    for jspec in joins_spec:
        left = str(jspec.get("left_label", "")).strip().upper()
        right = str(jspec.get("right_label", "")).strip().upper()
        left_col = str(jspec.get("left_col", "")).strip()
        right_col = str(jspec.get("right_col", "")).strip()
        jtype = str(jspec.get("type", "LEFT")).strip().upper()

        if left not in table_names or right not in table_names:
            raise ValueError("Join references an inaccessible table.")
        if jtype not in allowed_join_types:
            raise ValueError(f"Invalid join type: {jtype!r}")
        if left_col not in table_cols[left]:
            raise ValueError(
                f"Join column {left_col!r} not accessible for {left}."
            )
        if right_col not in table_cols[right]:
            raise ValueError(
                f"Join column {right_col!r} not accessible for {right}."
            )
        right_tname = table_names[right]
        join_clauses.append(
            f"{jtype} JOIN `{right_tname}` AS `_t_{right}` "
            f"ON `_t_{left}`.{q_id(left_col)} = `_t_{right}`.{q_id(right_col)}"
        )

    where_parts: List[str] = []
    params: Dict[str, Any] = {}
    param_idx = 0

    if "FINDEX" in table_names:
        run_ids_sorted = sorted(run_ids)
        if not run_ids_sorted:
            return "SELECT 0 AS cnt", {}
        params["_run_ids"] = run_ids_sorted
        where_parts.append("`_t_FINDEX`.`KW_RUN_ID` IN :_run_ids")

    for fspec in filters_spec:
        tlabel = str(fspec.get("table_label", "")).strip().upper()
        col = str(fspec.get("column", "")).strip()
        op_raw = str(fspec.get("op", "")).strip().upper()

        if tlabel not in table_names:
            raise ValueError(
                f"Filter references an inaccessible table: {tlabel!r}"
            )
        if col not in table_cols[tlabel]:
            raise ValueError(
                f"Filter column {col!r} not accessible for {tlabel}."
            )

        col_ref = f"`_t_{tlabel}`.{q_id(col)}"

        if op_raw in allowed_null_ops:
            where_parts.append(f"{col_ref} {op_raw}")
        elif op_raw in allowed_in_ops:
            raw_values = fspec.get("values") or []
            if not isinstance(raw_values, list):
                raw_values = [raw_values]
            values = [str(v) for v in raw_values if str(v).strip()]
            if not values:
                raise ValueError(
                    f"IN filter on {col!r} requires at least one value."
                )
            pname = f"p{param_idx}"
            param_idx += 1
            where_parts.append(f"{col_ref} {op_raw} :{pname}")
            params[pname] = values
        elif op_raw in allowed_ops:
            pname = f"p{param_idx}"
            param_idx += 1
            where_parts.append(f"{col_ref} {op_raw} :{pname}")
            params[pname] = fspec.get("value", "")
        else:
            raise ValueError(f"Invalid filter operator: {op_raw!r}")

    sql = f"SELECT COUNT(*) AS cnt\nFROM {from_clause}"
    for jc in join_clauses:
        sql += f"\n{jc}"
    if where_parts:
        sql += f'\nWHERE {" AND ".join(where_parts)}'

    return sql, params


def parse_text_presets(
    text: str, replace_fn: Callable[[str], str]
) -> List[Dict[str, str]]:
    """Parse a delimiter-based query preset text file."""
    delim = re.compile(r"^={4,}\s*$")
    presets: List[Dict[str, str]] = []
    lines = str(text or "").splitlines()
    i = 0
    while i < len(lines):
        if not delim.match(lines[i]):
            i += 1
            continue
        i += 1

        name_lines = []
        while i < len(lines) and not delim.match(lines[i]):
            name_lines.append(lines[i])
            i += 1
        name = " ".join(ln.strip() for ln in name_lines if ln.strip())
        if not name or i >= len(lines):
            continue
        i += 1

        sql_lines = []
        while i < len(lines) and not delim.match(lines[i]):
            sql_lines.append(lines[i])
            i += 1

        sql = "\n".join(ln.rstrip() for ln in sql_lines).strip()
        sql = replace_fn(sql)
        if name and sql:
            presets.append({"name": name, "query": sql})

    return presets


def load_query_db_presets(
    profile: Dict[str, Any],
    package_dir: Path,
    db_access_table_keys: Dict[str, str],
    profile_get_db: Callable[[dict, str, Any], Any],
) -> List[Dict[str, str]]:
    """Load query-db presets and replace table placeholders."""
    cfg = (
        profile.get("data", {}) if isinstance(profile.get("data"), dict) else {}
    )
    table_names: Dict[str, str] = {}
    for label, key in db_access_table_keys.items():
        tname = str(profile_get_db(cfg, key, "")).strip()
        if tname:
            table_names[label] = tname

    constants: Dict[str, str] = {}
    for key, value in cfg.items():
        skey = str(key).strip()
        if not skey:
            continue
        if value is None:
            constants[skey] = ""
        else:
            constants[skey] = str(value)
    for section_name in ("database", "paths", "general"):
        section = cfg.get(section_name, {})
        if not isinstance(section, dict):
            continue
        for key, value in section.items():
            skey = str(key).strip()
            if not skey or skey in constants:
                continue
            if value is None:
                constants[skey] = ""
            elif isinstance(value, list):
                constants[skey] = ",".join(str(v) for v in value)
            else:
                constants[skey] = str(value)

    def replace_placeholders(sql: str) -> str:
        if not isinstance(sql, str):
            return ""
        out = sql
        for key, value in constants.items():
            out = out.replace(f"{{{key}}}", value)
        for label, tname in table_names.items():
            out = out.replace(f"{{{label}}}", tname)
            out = out.replace(f"{{{label}_TABLENAME}}", tname)
        return out.strip()

    general_cfg = cfg.get("general", {})
    preset_filename = ""
    if isinstance(general_cfg, dict):
        preset_filename = str(
            general_cfg.get("db-query-preset-file")
            or general_cfg.get("db-query-preset_file")
            or general_cfg.get("db_query_preset_file")
            or ""
        ).strip()

    if not preset_filename:
        guessed = str(profile.get("profile_id", "")).strip()
        if guessed:
            preset_filename = f"{guessed}.txt"

    if preset_filename:
        text_path = (
            package_dir / "resources" / "aprofile_qdb_presets" / preset_filename
        )
        if text_path.exists():
            return parse_text_presets(
                text_path.read_text(encoding="utf-8"),
                replace_placeholders,
            )

    preset_path = package_dir / "resources" / "db_presets.yaml"
    if not preset_path.exists():
        return []

    try:
        with preset_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except Exception:
        return []

    presets: List[Dict[str, str]] = []

    if isinstance(raw, dict):
        iterator = raw.items()
    elif isinstance(raw, list):
        iterator = []
        for idx, entry in enumerate(raw):
            if isinstance(entry, dict):
                name = (
                    entry.get("name")
                    or entry.get("label")
                    or entry.get("title")
                    or f"Preset {idx + 1}"
                )
                iterator.append((name, entry))
    else:
        iterator = []

    for name, entry in iterator:
        query = ""
        if isinstance(entry, str):
            query = entry
        elif isinstance(entry, dict):
            query = entry.get("query") or entry.get("sql") or ""

        query = replace_placeholders(query)
        if not query:
            continue

        presets.append(
            {
                "name": str(name),
                "query": query,
            }
        )

    return presets

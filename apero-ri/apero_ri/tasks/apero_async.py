#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APERO RI: Async task management

Rules: Cannot import from apero_ri
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# =============================================================================
# Define variables
# =============================================================================



# =============================================================================
# Define global classes
# =============================================================================
class AperoAsyncTask:
    """Class representing an asynchronous task in APERO RI."""
    def __init__(self, name, description, status='pending'):
        # name and description
        self.name = name     
        self.description = description
        # Progress is a float between 0.0 and 1.0 representing the 
        # completion percentage
        self.progress = 0.0
        # Status can be 'pending', 'in_progress', 'completed', or 'failed'
        self.status = status
        # Long string (markdown) for writing the info page
        self.info = ''
        # list of output files this task produces (for use in the UI)
        self.output_files = []
        # last run (string "Never" or ISO timestamp of last run)
        self.last_run = 'Never'
        # number of times this task has been run
        self.run_count = 0

    def to_dict(self):
        """Convert the task to a dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'info': self.info,
            'last_run': self.last_run,
            'output_files': self.output_files,
            'run_count': self.run_count,
        }
        
    def run_job(self, params: Dict[str, Any]):
        raise NotImplementedError('Subclasses must implement the '
                                  'run_job method.')

 
# =============================================================================
# Define common functions
# =============================================================================
def database_query(params: Dict[str, Any], query: str):
    """
    Execute a database query with the given parameters.

    parameters:
    - DATABASE_MODE: str, mysql+pymysql
    - DATABASE_HOST: str, the database host, e.g. localhost
    - DATABASE_USER: str, the database user, e.g. root
    - DATABASE_PASSWORD: str, the database password, e.g. password
    - DATABASE_NAME: str, the database name to connect to

    :param params: A dictionary of parameters for the query.
    :param query: The database query string to execute.
    :return: For row-returning queries, a list of dictionaries.
             For non-row-returning queries, a dictionary with ``rowcount``.
    """
    from urllib.parse import quote_plus

    from sqlalchemy import create_engine, text

    required = [
        'DATABASE_MODE',
        'DATABASE_HOST',
        'DATABASE_USER',
        'DATABASE_PASSWORD',
        'DATABASE_NAME',
    ]
    missing = [key for key in required if not params.get(key)]
    if missing:
        raise ValueError(f"Missing database parameter(s): {', '.join(missing)}")

    mode = str(params['DATABASE_MODE'])
    host = str(params['DATABASE_HOST'])
    user = quote_plus(str(params['DATABASE_USER']))
    password = quote_plus(str(params['DATABASE_PASSWORD']))
    dbname = str(params['DATABASE_NAME'])

    db_url = f'{mode}://{user}:{password}@{host}/{dbname}'
    engine = create_engine(db_url, future=True)

    try:
        with engine.begin() as connection:
            result = connection.execute(text(query))
            if result.returns_rows:
                return [dict(row) for row in result.mappings().all()]
            return {'rowcount': result.rowcount}
    finally:
        engine.dispose()
        

def get_db_params(aparams: Dict[str, Any]):
    db_cfg = aparams.get('database', {})
    if not isinstance(db_cfg, dict):
        db_cfg = {}
    db_params = dict(db_cfg)
    for _k in ('DATABASE_MODE', 'DATABASE_HOST', 'DATABASE_PASSWORD',
               'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_USERNAME'):
        if _k not in db_params and aparams.get(_k):
            db_params[_k] = aparams.get(_k)
    if 'DATABASE_USERNAME' in db_params and 'DATABASE_USER' not in db_params:
        db_params['DATABASE_USER'] = db_params['DATABASE_USERNAME']
    return db_params


def save_results(filename: Path, results: Any, 
                 metadata: Optional[Dict[str, Any]] = None):
    """
    Save results to a file. This can be used to store results of a task for 
    later retrieval by the UI.

    :param filename: The path to the file where results should be saved.
    :param results: The results data to save (e.g. list of dicts, or any 
                    serializable data).
    :param metadata: Optional dictionary of metadata to save alongside the results.
    """
    def _json_default(value: Any):
        """Fallback serializer for common non-JSON-native values."""
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (datetime, )):
            return value.isoformat()
        return str(value)

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'row_count': len(results) if isinstance(results, list) else None,
        'schema_version': 1,
        'metadata': metadata or {},
        'rows': results,
    }
    
    with path.open('w', encoding='utf-8') as fobj:
        json.dump(payload, fobj, ensure_ascii=False, indent=2,
                  default=_json_default)
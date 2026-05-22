#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""APERO RI task to generate APERO check documentation pages."""

from pathlib import Path
from typing import Any, Dict, List

from apero_ri.apero_monitoring.tools import generate_check_docs as docs_tool
from apero_ri.tasks import apero_async

# =============================================================================
# Define variables
# =============================================================================
__NAME__ = 'apero_ri.tasks.apero_check_doc_tasks'

PARAM_LIST = ['TASK_CONFIG']
APERO_PROFILE_PARAM_LIST: List[str] = []
DEFAULT_FREQUENCY = 24.0
DEFAULT_ENABLED = True
TASK_TYPE = 'GLOBAL'
USE_SUBPROCESS = False
MULTI_PROCESS = False
LOCAL_TASK = True
FILTERS: List[str] = []


# =============================================================================
# Define classes
# =============================================================================
class GenerateCheckDocsTask(apero_async.AperoAsyncTask):
    """Generate markdown documentation for APERO monitoring checks."""

    def __init__(self, status: str = 'pending'):
        name = 'Generate APERO Check Docs'
        description = (
            'Generate markdown documentation pages for APERO '
            'monitoring checks.'
        )
        super().__init__(name, description, status)

    def run_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate APERO check documentation into the configured folder."""
        task_config = dict(params.get('TASK_CONFIG', {}) or {})
        output_dir = self._output_dir(task_config)
        count, files = docs_tool.generate_check_docs(output_dir)

        self.progress = 1.0
        self.subprogress = 1.0
        self.output_files = [str(path) for path in files]
        self.info = self._info_markdown(output_dir, count, files)

        return dict(
            count=count,
            output_dir=str(output_dir),
            files=self.output_files,
        )

    @staticmethod
    def _output_dir(task_config: Dict[str, Any]) -> Path:
        """Resolve the output directory for generated check docs."""
        raw_path = str(
            task_config.get(
                'output_dir',
                task_config.get('docs_output_dir', ''),
            )
            or ''
        ).strip()
        if raw_path == '':
            return docs_tool.DEFAULT_DOCS_DIR
        return Path(raw_path).expanduser().resolve()

    @staticmethod
    def _info_markdown(
        output_dir: Path,
        count: int,
        files: List[Path],
    ) -> str:
        """Build the task info markdown shown in the UI."""
        lines = []
        lines.append('## APERO Check Docs')
        lines.append('')
        lines.append(f'- Output directory: `{output_dir}`')
        lines.append(f'- Files written: `{count}`')
        if len(files) > 0:
            lines.append(f'- First file: `{files[0]}`')
        return '\n'.join(lines)
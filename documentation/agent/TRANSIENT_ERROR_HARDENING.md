# APERO v0.8 Transient Database Error Hardening

## Overview

Enhanced APERO v0.8's database layer to handle intermittent MySQL/MariaDB transient errors, specifically **errno 1146** (table doesn't exist) which occurs in rare race conditions. This prevents data loss and failed workflows when tables are temporarily unavailable or in transition.

## Problem Statement

### In v0.7
- Rare errors: `mysql.connector ProgrammingError 1146 (42S02): table doesn't exist`
- Table actually exists and the same SQL works before/after
- Happens rarely (~1 failure per ~24k calls)
- Causes data loss/failed workflows

### Root Cause
Transient MySQL/MariaDB visibility issues where a table briefly reports as non-existent despite existing and being accessible immediately before/after. This is particularly problematic in:
- High-concurrency environments
- Operations crossing database consistency points
- Table modifications (drop/recreate cycles)

## Solution Implemented

### 1. Transient Error Detection (`_is_transient_table_error`)
New helper function identifies transient table-missing errors:
- MySQL errno 1146 pattern matching
- SQLAlchemy `NoSuchTableError` detection
- Excludes persistent/logical errors

**File:** `apero-core/aperocore/core/drs_db.py` (lines 72-101)

```python
def _is_transient_table_error(exception: Exception) -> bool:
    """Detect transient table-missing errors (MySQL errno 1146)"""
```

### 2. Enhanced Retry Logic (`_retry_operation`)
Upgraded from basic connection-error retries to comprehensive strategy:

**File:** `apero-core/aperocore/core/drs_db.py` (lines 104-171)

#### Features:
- **Bounded Retries:** max 5 attempts (configurable per call)
- **Exponential Backoff with Jitter:**
  - Base: 0.05s
  - Growth: exponential (2^attempt)
  - Cap: 1.0s max
  - Jitter: 0-20% random to prevent thundering herd
- **Selective Retry:** Only for transient errors (errno 1146)
- **Preserved Behavior:**
  - Connection errors: original fixed delays
  - Non-transient DB exceptions: fail fast
  - Success: return immediately (no retry)

#### Backoff Schedule:
| Attempt | Delay (before jitter) | Max with jitter |
|---------|----------------------|-----------------|
| 0→1     | ~0.05s              | ~0.06s          |
| 1→2     | ~0.10s              | ~0.12s          |
| 2→3     | ~0.20s              | ~0.24s          |
| 3→4     | ~0.40s              | ~0.48s          |
| 4→5     | ~0.80s              | ~0.96s          |
| **Total** | **~1.55s**        | **~1.86s**      |

### 3. Improved Metadata Reflection (`_get_metadata`)
Hardened metadata caching/reflection:

**File:** `apero-core/aperocore/core/drs_db.py` (lines 348-398)

#### Changes:
- Increased max retries: 7 (vs 5 for normal ops) on metadata reflection
- Wrapped reflection in dedicated `_reflect_metadata()` closure
- Enhanced exception handling:
  - Transient errors: retry with exponential backoff
  - Persistent `NoSuchTableError`: return empty metadata (graceful degradation)
  - Other errors: fail fast
- Cache preservation across transient errors

### 4. Documentation & Testing
Created comprehensive test suite validating:
- ✓ Transient error detection
- ✓ Successful operations (no retry)
- ✓ Retry on transient errors
- ✓ Disable transient retry when needed
- ✓ Max retries enforcement
- ✓ Exponential backoff timing

**File:** `test_retry_logic.py` (all tests passing)

## Files Modified

### Core Changes
| File | Lines | Changes |
|------|-------|---------|
| `apero-core/aperocore/core/drs_db.py` | 19-20 | Added `import random` for jitter |
| `apero-core/aperocore/core/drs_db.py` | 72-101 | New `_is_transient_table_error()` function |
| `apero-core/aperocore/core/drs_db.py` | 104-171 | Enhanced `_retry_operation()` function |
| `apero-core/aperocore/core/drs_db.py` | 348-398 | Improved `_get_metadata()` method |

### Impact Scope
All database operations using `_retry_operation()` automatically benefit:
- `count()` - Row counting with conditions
- `has_table()` - Table existence checks
- `add_row()` / `add_rows()` - Inserts
- `set_row()` - Updates
- `delete_rows()` - Deletes
- `create_table()` - DDL operations
- All SQLAlchemy metadata reflection operations

## Backward Compatibility

✓ **Fully backward compatible**:
- Existing code requires no changes
- Default behavior preserved for non-transient errors
- Connection error handling unchanged
- New parameter is optional with safe defaults

## Configuration

No changes needed. Built-in defaults are:
- `max_retries=5` per operation
- `retry_transient_table_errors=True` (enabled by default)
- Exponential backoff with jitter (automatic)

Optional: Disable transient retries where needed:
```python
# Disable transient table error retries for specific operation
_retry_operation(my_func, retry_transient_table_errors=False)
```

## Error Reporting

Enhanced error context on final failure:
- Attempt count preserved in exception chain
- Original exception preserved (no masking)
- Timing information implicit in elapsed time between retries

## Testing

Run comprehensive test suite:
```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
python test_retry_logic.py
```

**Results (all passing):**
- ✓ Transient error detection
- ✓ Successful operations (no unnecessary retry)
- ✓ Exponential backoff with jitter
- ✓ Max retry limits
- ✓ Configurable retry behavior

## Validation

✓ Python syntax check: `py_compile` - PASSED
✓ Import validation: All functions importable - PASSED
✓ Comprehensive unit tests: 6/6 PASSED
✓ Test coverage:
  - Error detection logic
  - Retry semantics
  - Backoff timing
  - Configuration options
  - Failure modes

## Performance Impact

Minimal and only on errors:
- **Success path:** No change (single try, immediate return)
- **Transient error path:** 0-2 seconds retry window (vs immediate failure)
- **Connection error path:** Unchanged
- **Non-transient error path:** Unchanged (fail fast)

## Next Steps

1. **Immediate:** Deploy this change to v0.8
2. **Monitoring:** Track errno 1146 occurrence rate
3. **Tuning:** Adjust `max_retries` or backoff schedule if needed based on metrics
4. **Documentation:** Add to release notes for v0.8

## Summary

This hardening makes APERO v0.8 resilient to transient MySQL/MariaDB visibility issues that cause rare but severe data loss. The implementation:
- ✓ Targets only genuine transient errors (errno 1146)
- ✓ Uses proven exponential backoff with jitter strategy
- ✓ Preserves existing behavior for non-transient errors
- ✓ Requires zero code changes in consuming code
- ✓ Is fully tested and validated


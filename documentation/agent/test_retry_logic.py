#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for enhanced retry logic in drs_db.py

Tests the new transient table error handling and exponential backoff strategy.
"""

import sys
import time
from pathlib import Path

# Add the apero-core to path
apero_core = Path(__file__).parent / 'apero-core'
sys.path.insert(0, str(apero_core))

from aperocore.core import drs_db
from sqlalchemy.exc import NoSuchTableError, OperationalError


def test_is_transient_table_error():
    """Test the transient table error detection function"""
    print("Testing _is_transient_table_error()...")
    
    # Test NoSuchTableError
    error1 = NoSuchTableError('test_table')
    assert drs_db._is_transient_table_error(error1) == True, "Failed to detect NoSuchTableError"
    
    # Test MySQL errno 1146
    error2 = Exception("(1146): Table 'database.table' doesn't exist")
    assert drs_db._is_transient_table_error(error2) == True, "Failed to detect errno 1146"
    
    # Test 'no such table' string
    error3 = Exception("no such table error")
    assert drs_db._is_transient_table_error(error3) == True, "Failed to detect 'no such table'"
    
    # Test non-transient error
    error4 = Exception("Some other error")
    assert drs_db._is_transient_table_error(error4) == False, "Incorrectly identified non-transient error"
    
    print("  ✓ All transient error detection tests passed")


def test_retry_operation_success():
    """Test that successful operations don't retry"""
    print("Testing _retry_operation() with successful call...")
    
    call_count = [0]
    
    def successful_func():
        call_count[0] += 1
        return "success"
    
    result = drs_db._retry_operation(successful_func, max_retries=5)
    assert result == "success", "Should return success"
    assert call_count[0] == 1, "Should only call function once"
    
    print("  ✓ Successful operation test passed")


def test_retry_operation_transient_error():
    """Test retry on transient table errors"""
    print("Testing _retry_operation() with transient table error...")
    
    call_count = [0]
    
    def failing_then_success():
        call_count[0] += 1
        if call_count[0] < 3:
            raise NoSuchTableError("test_table")
        return "success"
    
    start_time = time.time()
    result = drs_db._retry_operation(failing_then_success, max_retries=5,
                                     retry_transient_table_errors=True)
    elapsed = time.time() - start_time
    
    assert result == "success", "Should return success after retries"
    assert call_count[0] == 3, f"Should call function 3 times, got {call_count[0]}"
    assert elapsed > 0.05, f"Should have delays between retries, elapsed: {elapsed}"
    
    print(f"  ✓ Transient error retry test passed (took {elapsed:.2f}s with exponential backoff)")


def test_retry_operation_disable_transient_retry():
    """Test that transient table errors can be disabled"""
    print("Testing _retry_operation() with transient errors disabled...")
    
    call_count = [0]
    
    def failing_func():
        call_count[0] += 1
        raise NoSuchTableError("test_table")
    
    try:
        drs_db._retry_operation(failing_func, max_retries=5,
                               retry_transient_table_errors=False)
        assert False, "Should have raised NoSuchTableError"
    except NoSuchTableError:
        pass
    
    assert call_count[0] == 1, "Should fail fast when retries disabled"
    
    print("  ✓ Disabled transient error retry test passed")


def test_retry_operation_max_retries():
    """Test that operation fails after max retries"""
    print("Testing _retry_operation() max retries limit...")
    
    call_count = [0]
    
    def always_failing():
        call_count[0] += 1
        raise NoSuchTableError("test_table")
    
    try:
        drs_db._retry_operation(always_failing, max_retries=3,
                               retry_transient_table_errors=True)
        assert False, "Should have raised NoSuchTableError"
    except NoSuchTableError:
        pass
    
    assert call_count[0] == 3, f"Should retry 3 times, got {call_count[0]}"
    
    print("  ✓ Max retries limit test passed")


def test_exponential_backoff():
    """Test exponential backoff timing"""
    print("Testing exponential backoff timing...")
    
    call_count = [0]
    
    def always_failing():
        call_count[0] += 1
        raise NoSuchTableError("test_table")
    
    start_time = time.time()
    try:
        # Attempt 0: error -> sleep ~0.05s
        # Attempt 1: error -> sleep ~0.10s
        # Attempt 2: error -> raise
        drs_db._retry_operation(always_failing, max_retries=3,
                               retry_transient_table_errors=True)
    except NoSuchTableError:
        pass
    
    elapsed = time.time() - start_time
    # Expected: 0.05 + 0.1 = 0.15s (plus jitter and overhead)
    # Allow for up to 0.3s to account for jitter and system overhead
    assert elapsed < 0.5, f"Backoff timing seems off: {elapsed:.2f}s"
    assert elapsed > 0.1, f"Should have slept for backoff: {elapsed:.2f}s"
    
    print(f"  ✓ Exponential backoff test passed (elapsed: {elapsed:.2f}s)")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("APERO v0.8 Enhanced Retry Logic Test Suite")
    print("="*70 + "\n")
    
    try:
        test_is_transient_table_error()
        test_retry_operation_success()
        test_retry_operation_transient_error()
        test_retry_operation_disable_transient_retry()
        test_retry_operation_max_retries()
        test_exponential_backoff()
        
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


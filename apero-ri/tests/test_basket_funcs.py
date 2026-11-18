"""Tests for basket entry limits and persistence helpers."""

from apero_ri.core import basket_funcs as basket


def test_add_to_basket_stops_at_file_limit(monkeypatch) -> None:
    """Only add unique accessible entries while the basket has room."""
    existing = [
        {
            'profile_id': 'profile',
            'obs_dir': 'night',
            'filename': f'file-{index}.fits',
        }
        for index in range(basket.BASKET_FILE_LIMIT - 1)
    ]
    duplicate = dict(existing[0], kw_run_id='R1')
    candidate_one = {
        'profile_id': 'profile',
        'obs_dir': 'night',
        'filename': 'new-one.fits',
        'kw_run_id': 'R1',
    }
    candidate_two = dict(candidate_one, filename='new-two.fits')
    saved = []
    monkeypatch.setattr(basket, 'load_basket', lambda username: existing)
    monkeypatch.setattr(
        basket, 'save_basket',
        lambda username, entries: saved.extend(entries),
    )

    added = basket.add_to_basket(
        'alice', [duplicate, candidate_one, candidate_two], {'R1'}
    )

    assert added == 1
    assert len(saved) == basket.BASKET_FILE_LIMIT
    assert saved[-1]['filename'] == 'new-one.fits'


def test_filter_accessible_rows_includes_same_object_combined_products() -> None:
    """Authorize NULL-RUN products from any directly accessible object row."""
    rows = [
        {
            'FILENAME': 'source.fits',
            'KW_OBJNAME': 'GL699',
            'KW_RUN_ID': 'R1',
        },
        {
            'FILENAME': 'template.fits',
            'KW_OBJNAME': 'GL699',
            'KW_RUN_ID': None,
        },
        {
            'FILENAME': 'private.fits',
            'KW_OBJNAME': 'GL699',
            'KW_RUN_ID': 'PRIVATE',
        },
        {
            'FILENAME': 'other-template.fits',
            'KW_OBJNAME': 'OTHER',
            'KW_RUN_ID': None,
        },
        {
            'FILENAME': 'no-object.fits',
            'KW_RUN_ID': None,
        },
    ]

    filtered = basket.filter_accessible_rows(rows, {'R1'})

    assert [row['FILENAME'] for row in filtered] == [
        'source.fits', 'template.fits']
    assert filtered[1]['ACCESS_RUN_ID'] == 'R1'
    assert filtered[1]['KW_RUN_ID'] is None


def test_filter_accessible_rows_supports_legacy_object_cache() -> None:
    """Authorize old object-scoped rows that predate the KW_OBJNAME column."""
    rows = [
        {'FILENAME': 'source.fits', 'KW_RUN_ID': 'R1'},
        {'FILENAME': 'template.fits', 'KW_RUN_ID': None},
    ]

    filtered = basket.filter_accessible_rows(
        rows, {'R1'}, object_name='GL699'
    )

    assert [row['FILENAME'] for row in filtered] == [
        'source.fits', 'template.fits']
    assert all(row['ACCESS_RUN_ID'] == 'R1' for row in filtered)
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
(function () {
    'use strict';

    var cfg = window.ARI_FAV_OBJECTS || {};
    var profileId = String(cfg.profileId || '').trim();
    var removeApiUrl = String(cfg.removeApiUrl || '').trim();
    var reorderApiUrl = String(cfg.reorderApiUrl || '').trim();

    var listEl = document.getElementById('fav-objects-list');
    var emptyEl = document.getElementById('fav-empty');
    var countEl = document.getElementById('fav-objects-count');
    var removeAllBtn = document.getElementById('fav-remove-all-btn');

    if (!listEl || !profileId || !removeApiUrl) {
        return;
    }

    function listCards() {
        return Array.prototype.slice.call(
            listEl.querySelectorAll('.ari-fav-card[data-objname]')
        );
    }

    function updateState() {
        var cards = listCards();
        var count = cards.length;
        if (countEl) {
            countEl.textContent = String(count);
        }
        if (emptyEl) {
            emptyEl.style.display = count ? 'none' : '';
        }
        if (removeAllBtn) {
            removeAllBtn.disabled = (count === 0);
        }
    }

    function orderedObjectNames() {
        return listCards()
            .map(function (card) {
                return String(card.getAttribute('data-objname') || '').trim();
            })
            .filter(function (name) { return !!name; });
    }

    function removeCard(objname) {
        var card = listEl.querySelector(
            '.ari-fav-card[data-objname="' + CSS.escape(objname) + '"]'
        );
        if (card && card.parentNode) {
            card.parentNode.removeChild(card);
        }
        updateState();
    }

    async function removeFavourite(objname) {
        var response = await fetch(removeApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_id: profileId,
                objname: objname,
            })
        });
        var payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || 'Could not remove favourite object');
        }
    }

    async function reorderFavourites(objnames) {
        if (!reorderApiUrl) {
            return;
        }
        var response = await fetch(reorderApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile_id: profileId,
                objnames: objnames,
            })
        });
        var payload = await response.json();
        if (!payload.success) {
            throw new Error(payload.error || 'Could not reorder favourite objects');
        }
    }

    function shouldIgnoreCardClick(target) {
        if (!(target instanceof Element)) {
            return false;
        }
        return !!target.closest('.fav-remove-btn, .ari-fav-card__drag');
    }

    function armCardForDrag(card) {
        if (!(card instanceof Element)) {
            return;
        }
        card.setAttribute('data-drag-armed', '1');
    }

    function disarmCardDrag(card) {
        if (!(card instanceof Element)) {
            return;
        }
        card.removeAttribute('data-drag-armed');
    }

    function wireCardEvents(card) {
        if (!(card instanceof Element)) {
            return;
        }

        var openUrl = String(card.getAttribute('data-open-url') || '').trim();
        if (openUrl) {
            card.addEventListener('click', function (ev) {
                if (shouldIgnoreCardClick(ev.target)) {
                    return;
                }
                window.location.href = openUrl;
            });
        }

        var dragHandle = card.querySelector('.ari-fav-card__drag');
        var removeBtn = card.querySelector('.fav-remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', async function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                var objname = String(removeBtn.getAttribute('data-objname') || '').trim();
                if (!objname) {
                    return;
                }
                removeBtn.disabled = true;
                try {
                    await removeFavourite(objname);
                    removeCard(objname);
                } catch (err) {
                    window.alert(err.message || 'Could not remove favourite object.');
                    removeBtn.disabled = false;
                }
            });
        }

        if (!dragHandle) {
            return;
        }

        dragHandle.addEventListener('mousedown', function (ev) {
            ev.stopPropagation();
            armCardForDrag(card);
        });
        dragHandle.addEventListener('pointerdown', function (ev) {
            ev.stopPropagation();
            armCardForDrag(card);
        });
        dragHandle.addEventListener('touchstart', function (ev) {
            ev.stopPropagation();
            armCardForDrag(card);
        });
        dragHandle.addEventListener('click', function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
        });
        dragHandle.addEventListener('dragstart', function (ev) {
            ev.stopPropagation();
        });

        card.addEventListener('dragstart', function (ev) {
            if (card.getAttribute('data-drag-armed') !== '1') {
                ev.preventDefault();
                return;
            }
            card.classList.add('is-dragging');
            ev.dataTransfer.effectAllowed = 'move';
            ev.dataTransfer.setData('text/plain',
                String(card.getAttribute('data-objname') || ''));
        });

        card.addEventListener('dragend', function () {
            card.classList.remove('is-dragging');
            disarmCardDrag(card);
        });

        card.addEventListener('mouseup', function () {
            if (!card.classList.contains('is-dragging')) {
                disarmCardDrag(card);
            }
        });
    }

    listEl.addEventListener('dragover', function (ev) {
        ev.preventDefault();
        var dragging = listEl.querySelector('.ari-fav-card.is-dragging');
        if (!dragging) {
            return;
        }
        var target = ev.target.closest('.ari-fav-card[data-objname]');
        if (!target || target === dragging || target.parentNode !== listEl) {
            return;
        }

        var rect = target.getBoundingClientRect();
        var insertBefore = ev.clientY < (rect.top + rect.height / 2);
        if (insertBefore) {
            listEl.insertBefore(dragging, target);
        } else {
            listEl.insertBefore(dragging, target.nextSibling);
        }
    });

    listEl.addEventListener('drop', async function (ev) {
        ev.preventDefault();
        var dragging = listEl.querySelector('.ari-fav-card.is-dragging');
        if (!dragging) {
            return;
        }
        try {
            await reorderFavourites(orderedObjectNames());
        } catch (err) {
            window.alert(err.message || 'Could not reorder favourites.');
        }
    });

    // Delegated click handler keeps card navigation robust even if a card's
    // individual handler was not wired for any reason.
    listEl.addEventListener('click', function (ev) {
        var target = ev.target;
        if (!(target instanceof Element)) {
            return;
        }
        if (shouldIgnoreCardClick(target)) {
            return;
        }
        var card = target.closest('.ari-fav-card[data-open-url]');
        if (!card) {
            return;
        }
        var openUrl = String(card.getAttribute('data-open-url') || '').trim();
        if (!openUrl) {
            return;
        }
        window.location.href = openUrl;
    });

    document.addEventListener('mouseup', function () {
        listCards().forEach(function (card) {
            if (!card.classList.contains('is-dragging')) {
                disarmCardDrag(card);
            }
        });
    });

    if (removeAllBtn) {
        removeAllBtn.addEventListener('click', async function () {
            var names = orderedObjectNames();
            if (!names.length) {
                return;
            }
            var confirmed = window.confirm(
                'Remove all ' + names.length + ' favourite objects for this profile?'
            );
            if (!confirmed) {
                return;
            }

            removeAllBtn.disabled = true;
            try {
                for (var i = 0; i < names.length; i += 1) {
                    var objname = names[i];
                    await removeFavourite(objname);
                    removeCard(objname);
                }
            } catch (err) {
                window.alert(err.message || 'Could not remove all favourite objects.');
            } finally {
                updateState();
            }
        });
    }

    listCards().forEach(wireCardEvents);

    updateState();
})();

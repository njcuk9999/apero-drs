/* Floating page pin action */
(function () {
	function bookmarkIconSvg(isPinned) {
		if (isPinned) {
			return '' +
				'<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">' +
				'<path d="M6 3.25h8a1.75 1.75 0 0 1 1.75 1.75v11.7l-5.75-3.35-5.75 3.35V5A1.75 1.75 0 0 1 6 3.25z" fill="currentColor"></path>' +
				'</svg>';
		}
		return '' +
			'<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">' +
			'<path d="M6 3.25h8a1.75 1.75 0 0 1 1.75 1.75v11.7l-5.75-3.35-5.75 3.35V5A1.75 1.75 0 0 1 6 3.25z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"></path>' +
			'</svg>';
	}

	function shouldEnablePins(meta) {
		if (!meta || !meta.loggedIn || !meta.pageId) {
			return false;
		}
		if (meta.pageId === 'home.login' || meta.pageId === 'home.logout') {
			return false;
		}
		return true;
	}

	function normalizePageLabel(meta) {
		if (meta && meta.pageLabel && String(meta.pageLabel).trim()) {
			return String(meta.pageLabel).trim();
		}
		var headerEl = document.querySelector('.ari-page-header h1') ||
			document.querySelector('.ari-main h1') ||
			document.querySelector('main h1');
		if (!headerEl) {
			return 'Pinned Page';
		}
		var text = (headerEl.textContent || '').replace(/\s+/g, ' ').trim();
		return text || 'Pinned Page';
	}

	async function fetchPins() {
		var response = await fetch('/api/user/pins/list');
		var payload = await response.json();
		if (!payload.success) {
			throw new Error(payload.error || 'Failed to load pinned pages');
		}
		return payload.pins || [];
	}

	async function togglePin(payload) {
		var response = await fetch('/api/user/pins/toggle', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});
		var data = await response.json();
		if (!data.success) {
			throw new Error(data.error || 'Failed to toggle page pin');
		}
		return data;
	}

	function renderState(button, pinned) {
		button.classList.toggle('is-pinned', !!pinned);
		button.setAttribute('aria-pressed', pinned ? 'true' : 'false');
		button.title = pinned ? 'Pinned page (click to remove)' : 'Pin this page';
		button.setAttribute('aria-label', button.title);
		button.innerHTML = '<span class="ari-page-pin-fab__icon" aria-hidden="true">' +
			bookmarkIconSvg(!!pinned) + '</span>';
	}

	document.addEventListener('DOMContentLoaded', async function () {
		var meta = window.ARI_PAGE_META || null;
		if (!shouldEnablePins(meta)) {
			return;
		}

		var mainContent = document.querySelector('.ari-main');
		if (!mainContent) {
			return;
		}

		if (mainContent.querySelector('.ari-page-pin-fab')) {
			return;
		}

		var button = document.createElement('button');
		button.type = 'button';
		button.className = 'ari-page-pin-fab';
		mainContent.appendChild(button);

		var currentPage = {
			page_id: String(meta.pageId),
			label: normalizePageLabel(meta),
			icon: meta.pageIcon || 'fa-solid fa-bookmark',
			url: window.location.pathname + window.location.search
		};

		try {
			var pins = await fetchPins();
			var isPinned = pins.some(function (pin) {
				return pin.page_id === currentPage.page_id;
			});
			renderState(button, isPinned);
		} catch (err) {
			button.remove();
			return;
		}

		var busy = false;
		button.addEventListener('click', async function () {
			if (busy) {
				return;
			}
			busy = true;
			button.disabled = true;
			try {
				var result = await togglePin(currentPage);
				renderState(button, result.pinned);
			} catch (err) {
				window.alert(err.message || 'Could not update pin state.');
			} finally {
				busy = false;
				button.disabled = false;
			}
		});
	});
})();

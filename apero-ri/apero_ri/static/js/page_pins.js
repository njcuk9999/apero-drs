/* Floating page pin action */
(function () {
	function iconSpan(html) {
		return '<span class="ari-page-pin-fab__icon" aria-hidden="true">' + html + '</span>';
	}

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

	function favouriteIconSvg(isFavourite) {
		if (isFavourite) {
			return '' +
				'<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">' +
				'<path d="M10 2.4l2.2 4.45 4.9.71-3.55 3.46.84 4.88L10 13.57 5.61 15.9l.84-4.88L2.9 7.56l4.9-.71L10 2.4z" fill="currentColor"></path>' +
				'</svg>';
		}
		return '' +
			'<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">' +
			'<path d="M10 2.4l2.2 4.45 4.9.71-3.55 3.46.84 4.88L10 13.57 5.61 15.9l.84-4.88L2.9 7.56l4.9-.71L10 2.4z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"></path>' +
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

	function shouldEnableApi(meta) {
		if (!meta || !meta.pageId) {
			return false;
		}
		return !!resolveApiContext(meta);
	}

	function shouldEnableIssue(meta) {
		if (!meta || !meta.loggedIn || !meta.pageId) {
			return false;
		}
		if (meta.pageId === 'home.login'
				|| meta.pageId === 'home.logout') {
			return false;
		}
		return true;
	}

	function shouldEnableFavourite(meta) {
		if (!meta || !meta.loggedIn) {
			return false;
		}
		var cfg = window.ARI_OBJECT_PAGE || null;
		if (!cfg) {
			return false;
		}
		if (!cfg.profileId || !cfg.objname) {
			return false;
		}
		if (!cfg.objectFavouriteApiGet || !cfg.objectFavouriteApiToggle) {
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

	async function fetchFavouriteState(cfg) {
		var url = String(cfg.objectFavouriteApiGet)
			+ '?profile_id=' + encodeURIComponent(String(cfg.profileId || ''))
			+ '&objname=' + encodeURIComponent(String(cfg.objname || ''));
		var response = await fetch(url);
		var payload = await response.json();
		if (!payload.success) {
			throw new Error(payload.error || 'Failed to load favourites');
		}
		return !!(payload.favourite_objects && payload.favourite_objects.is_favourite);
	}

	async function toggleFavourite(cfg) {
		var response = await fetch(String(cfg.objectFavouriteApiToggle || ''), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				profile_id: String(cfg.profileId || ''),
				objname: String(cfg.objname || ''),
			})
		});
		var payload = await response.json();
		if (!payload.success) {
			throw new Error(payload.error || 'Failed to update favourites');
		}
		return !!payload.favourite;
	}

	function renderState(button, pinned) {
		button.classList.toggle('is-pinned', !!pinned);
		button.setAttribute('aria-pressed', pinned ? 'true' : 'false');
		button.title = pinned ? 'Pinned page (click to remove)' : 'Pin this page';
		button.setAttribute('aria-label', button.title);
		button.innerHTML = iconSpan(bookmarkIconSvg(!!pinned));
	}

	function renderFavouriteState(button, favourite) {
		button.classList.toggle('is-favourite', !!favourite);
		button.setAttribute('aria-pressed', favourite ? 'true' : 'false');
		button.title = favourite
			? 'Object is in favourites (click to remove)'
			: 'Add object to favourites';
		button.setAttribute('aria-label', button.title);
		button.innerHTML = iconSpan(favouriteIconSvg(!!favourite));
	}

	function quotePy(value) {
		return '\'' + String(value === null || value === undefined ? '' : value)
			.replace(/\\/g, '\\\\')
			.replace(/'/g, "\\'") + '\'';
	}

	function pyDict(obj) {
		var keys = Object.keys(obj || {});
		if (!keys.length) {
			return '{}';
		}
		keys.sort();
		return '{' + keys.map(function (k) {
			return quotePy(k) + ': ' + quotePy(obj[k]);
		}).join(', ') + '}';
	}

	function currentActiveObjectTab() {
		var activeBtn = document.querySelector('#op-tabs .ari-sg-tab--active');
		if (!activeBtn) return 'all';
		return String(activeBtn.getAttribute('data-tab') || 'all').trim() || 'all';
	}

	function collectTableColumnFilters() {
		var out = {};
		document.querySelectorAll('#ot-filter-row input[data-col], #ot-filter-row select[data-col]').forEach(function (el) {
			if (!(el instanceof Element)) return;
			var col = String(el.getAttribute('data-col') || '').trim();
			if (!col) return;
			var val = String(el.value || '').trim();
			if (!val) return;
			out[col] = val;
		});
		return out;
	}

	function resolveApiContext(meta) {
		var pageId = String((meta && meta.pageId) || '');
		var path = String(window.location.pathname || '');
		var ctx = {
			pageId: pageId,
			path: path,
			baseUrl: window.location.origin,
			profileId: '',
			objname: '',
			pageType: '',
			tab: '',
		};

		if (window.ARI_OBJECT_PAGE) {
			ctx.pageType = 'object_page';
			ctx.profileId = String(window.ARI_OBJECT_PAGE.profileId || '');
			ctx.objname = String(window.ARI_OBJECT_PAGE.objname || '');
			ctx.tab = currentActiveObjectTab();
			return ctx;
		}

		if (window.ARI_BASKET) {
			ctx.pageType = 'basket';
			ctx.profileId = String(window.ARI_BASKET.profileId || '');
			return ctx;
		}

		if (window.ARI_OBJ_TABLE) {
			ctx.profileId = String(window.ARI_OBJ_TABLE.profileId || '');
			if (path.indexOf('/observation-table') !== -1) {
				ctx.pageType = 'obs_table';
			} else {
				ctx.pageType = 'object_table';
			}
			return ctx;
		}

		if (window.ARI_ASTROMETRICS) {
			ctx.pageType = 'astrometrics';
			ctx.profileId = String(
				window.ARI_ASTROMETRICS.profileId || '');
			ctx.instrument = String(
				window.ARI_ASTROMETRICS.instrument || '');
			var activeTab = document.querySelector(
				'.ari-htab.ari-htab--active');
			ctx.tab = activeTab
				? String(activeTab.getAttribute('data-htab') || '')
				: '';
			return ctx;
		}

		var parts = pageId.split('.');
		if (parts.length >= 4 && parts[0] === 'home' && parts[1] === 'data_portal') {
			ctx.profileId = parts[2] || '';
			if (parts[3] === 'object_table') ctx.pageType = 'object_table';
			if (parts[3] === 'obs_table') ctx.pageType = 'obs_table';
			if (parts[3] === 'basket') ctx.pageType = 'basket';
		}

		return ctx.pageType ? ctx : null;
	}

	function buildObjectTableExample(ctx) {
		var colFilters = collectTableColumnFilters();
		return {
			title: 'Object Table API Example',
			description: 'Fetch object-table rows for this profile, then apply currently selected table filters as a pandas mask.',
			code: [
				'from apero_ri import ari_api',
				'import pandas as pd',
				'',
				'profile = ari_api.AperoProfile(' + quotePy(ctx.profileId) + ')',
				'df = profile.get_object_table(fmt=' + quotePy('pandas') + ')',
				'',
				'# Optional mask from current table filters in the UI',
				'filters = ' + pyDict(colFilters),
				'if not df.empty and filters:',
				'    mask = pd.Series(True, index=df.index)',
				'    for col, value in filters.items():',
				'        if col in df.columns and str(value):',
				'            mask &= df[col].astype(str).str.contains(',
				'                str(value), case=False, na=False',
				'            )',
				'    df = df.loc[mask]',
				'',
				'print(f"Rows: {len(df)}")',
				'print(df.head())',
			].join('\n'),
		};
	}

	function buildObsTableExample(ctx) {
		var colFilters = collectTableColumnFilters();
		return {
			title: 'Observation Table API Example',
			description: 'Fetch observation-table rows for this profile, then apply currently selected table filters as a pandas mask.',
			code: [
				'from apero_ri import ari_api',
				'import pandas as pd',
				'',
				'profile = ari_api.AperoProfile(' + quotePy(ctx.profileId) + ')',
				'df = profile.get_observation_table(fmt=' + quotePy('pandas') + ')',
				'',
				'# Optional mask from current table filters in the UI',
				'filters = ' + pyDict(colFilters),
				'if not df.empty and filters:',
				'    mask = pd.Series(True, index=df.index)',
				'    for col, value in filters.items():',
				'        if col in df.columns and str(value):',
				'            mask &= df[col].astype(str).str.contains(',
				'                str(value), case=False, na=False',
				'            )',
				'    df = df.loc[mask]',
				'',
				'print(f"Rows: {len(df)}")',
				'print(df.head())',
			].join('\n'),
		};
	}

	function buildBasketExample(ctx) {
		return {
			title: 'Download Basket API Example (GL699)',
			description: 'Example showing GL699 download via the ARI client (uses the basket internally).',
			code: [
				'from apero_ri import ari_api',
				'',
				'profile = ari_api.AperoProfile(' + quotePy(ctx.profileId) + ')',
				'obj = profile.get_object(' + quotePy('GL699') + ')',
				'',
				'# Count matching files before download',
				'count = obj.get_count(preset=' + quotePy('ccf') + ', OBS_DIR=' + quotePy('2020-08-31') + ')',
				'print("Matching files:", count)',
				'',
				'# Download files (basket compile + download handled internally)',
				'files = obj.get_data(',
				'    localdir=' + quotePy('/tmp/gl699_ccf') + ',',
				'    preset=' + quotePy('ccf') + ',',
				'    OBS_DIR=' + quotePy('2020-08-31') + ',',
				')',
				'print("Downloaded:", len(files))',
			].join('\n'),
		};
	}

	function buildObjectPageExample(ctx) {
		var tab = ctx.tab || 'all';
		var profileId = ctx.profileId;
		var objname = ctx.objname;
		var ccfStart = '';
		var ccfEnd = '';
		var ccfNobs = '';
		var startEl = document.getElementById('op-ccf-mjd-start');
		var endEl = document.getElementById('op-ccf-mjd-end');
		var nobsEl = document.getElementById('op-ccf-nobs');
		if (startEl) ccfStart = String(startEl.value || '').trim();
		if (endEl) ccfEnd = String(endEl.value || '').trim();
		if (nobsEl) ccfNobs = String(nobsEl.value || '').trim();

		function baseIntro() {
			return [
				'from apero_ri import ari_api',
				'import pandas as pd',
				'',
				'profile = ari_api.AperoProfile(' + quotePy(profileId) + ')',
				'obj = profile.get_object(' + quotePy(objname) + ')',
				'',
			];
		}

		if (tab === 'all') {
			return {
				title: 'Object Page API Example (All Tab)',
				description: 'Fetch the full object class payload for this profile/object.',
				code: baseIntro().concat([
					'rows = obj.target_info(fmt=' + quotePy('dict') + ')',
					'sections = sorted({str(r.get(' + quotePy('section') + ', ' + quotePy('') + ')) for r in rows})',
					'print("Available sections:", sections)',
				]).join('\n'),
			};
		}

		if (tab === 'target_info') {
			return {
				title: 'Object Page API Example (Target Info)',
				description: 'Fetch target/object metadata for this profile/object.',
				code: baseIntro().concat([
					'df = obj.target_info(fmt=' + quotePy('pandas') + ')',
					'target_info = df[df[' + quotePy('section') + '] == ' + quotePy('target_info') + ']',
					'print(target_info)',
				]).join('\n'),
			};
		}

		if (tab === 'spectrum') {
			return {
				title: 'Object Page API Example (Spectrum Tab)',
				description: 'Fetch spectrum-related section rows and file list for this object.',
				code: baseIntro().concat([
					'df = obj.target_info(fmt=' + quotePy('pandas') + ')',
					'spectrum_info = df[df[' + quotePy('section') + '] == ' + quotePy('spectrum') + ']',
					'print(spectrum_info)',
					'',
					'files_default = obj.list_files(preset=' + quotePy('default') + ')',
					'print("Default-preset files:", len(files_default))',
				]).join('\n'),
			};
		}

		if (tab === 'ccf') {
			return {
				title: 'Object Page API Example (CCF Tab)',
				description: 'Work with CCF rows via file-browser preset ccf and current UI selection hints.',
				code: baseIntro().concat([
					'ccf_rows = obj.list_files(preset=' + quotePy('ccf') + ')',
					'ccf_df = pd.DataFrame(ccf_rows)',
					'print("CCF rows:", len(ccf_df))',
					'',
					'# Current UI controls (for reproducibility notes)',
					'ccf_start = ' + quotePy(ccfStart || '') ,
					'ccf_end = ' + quotePy(ccfEnd || ''),
					'ccf_nobs = ' + quotePy(ccfNobs || ''),
					'print({"start": ccf_start, "end": ccf_end, "nobs": ccf_nobs})',
				]).join('\n'),
			};
		}

		if (tab === 'time_series') {
			return {
				title: 'Object Page API Example (Time Series Tab)',
				description: 'Fetch and inspect time-series section rows for this object.',
				code: baseIntro().concat([
					'df = obj.target_info(fmt=' + quotePy('pandas') + ')',
					'ts = df[df[' + quotePy('section') + '] == ' + quotePy('time_series') + ']',
					'print(ts)',
				]).join('\n'),
			};
		}

		if (tab === 'lbl') {
			return {
				title: 'Object Page API Example (LBL Tab)',
				description: 'Fetch and inspect LBL section rows for this object.',
				code: baseIntro().concat([
					'df = obj.target_info(fmt=' + quotePy('pandas') + ')',
					'lbl = df[df[' + quotePy('section') + '] == ' + quotePy('lbl') + ']',
					'print(lbl)',
				]).join('\n'),
			};
		}

		if (tab === 'file_browser') {
			return {
				title: 'Object Page API Example (File Browser Tab)',
				description: 'Fetch file-browser rows for this profile/object using the ARI client.',
				code: baseIntro().concat([
					'rows = obj.list_files(preset=' + quotePy('default') + ')',
					'print("Rows:", len(rows))',
					'if rows:',
					'    print(rows[0])',
				]).join('\n'),
			};
		}

		if (tab === 'download') {
			return {
				title: 'Object Page API Example (Download Tab)',
				description: 'Preview and download files for this object using ARI client methods.',
				code: baseIntro().concat([
					'count = obj.get_count(preset=' + quotePy('default') + ')',
					'print("Default-preset downloadable files:", count)',
					'',
					'# Download selected files (example: tcorr files only)',
					'files = obj.get_data(',
					'    localdir=' + quotePy('/tmp/object_download') + ',',
					'    preset=' + quotePy('default') + ',',
					'    KW_OUTPUT=' + quotePy('TCORR') + ',',
					')',
					'print("Downloaded:", len(files))',
				]).join('\n'),
			};
		}

		if (tab === 'debug') {
			return {
				title: 'Object Page API Example (Debug Tab)',
				description: 'Inspect object rows and files relevant for debug analysis.',
				code: baseIntro().concat([
					'df = obj.target_info(fmt=' + quotePy('pandas') + ')',
					'print(df.head())',
					'',
					'tcorr_rows = obj.list_files(preset=' + quotePy('tcorr') + ')',
					'print("TCORR rows:", len(tcorr_rows))',
				]).join('\n'),
			};
		}

		return {
			title: 'Object Page API Example',
			description: 'Fetch object-page payload for this profile/object.',
			code: baseIntro().concat([
				'rows = obj.target_info(fmt=' + quotePy('dict') + ')',
				'print(rows[:5])',
			]).join('\n'),
		};
	}

	function pyEscape(s) {
		return String(s)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;');
	}

	function highlightPythonLine(line) {
		var keywords = {
			False: 1, None: 1, True: 1, and: 1, as: 1, assert: 1, async: 1,
			await: 1, break: 1, class: 1, continue: 1, def: 1, del: 1,
			elif: 1, else: 1, except: 1, finally: 1, for: 1, from: 1,
			global: 1, if: 1, import: 1, in: 1, is: 1, lambda: 1,
			nonlocal: 1, not: 1, or: 1, pass: 1, raise: 1, return: 1,
			try: 1, while: 1, with: 1, yield: 1,
		};
		var builtins = {
			print: 1, len: 1, list: 1, dict: 1, str: 1, int: 1, float: 1,
			set: 1, sorted: 1, pd: 1,
		};

		var out = '';
		var i = 0;
		while (i < line.length) {
			var ch = line.charAt(i);

			if (ch === '#') {
				out += '<span class="ari-py-cmt">' + pyEscape(line.slice(i)) + '</span>';
				break;
			}

			if (ch === '"' || ch === '\'') {
				var q = ch;
				var j = i + 1;
				while (j < line.length) {
					var cj = line.charAt(j);
					if (cj === '\\') {
						j += 2;
						continue;
					}
					if (cj === q) {
						j += 1;
						break;
					}
					j += 1;
				}
				out += '<span class="ari-py-str">' + pyEscape(line.slice(i, j)) + '</span>';
				i = j;
				continue;
			}

			if (/[A-Za-z_]/.test(ch)) {
				var k = i + 1;
				while (k < line.length && /[A-Za-z0-9_]/.test(line.charAt(k))) {
					k += 1;
				}
				var word = line.slice(i, k);
				if (keywords[word]) {
					out += '<span class="ari-py-kw">' + pyEscape(word) + '</span>';
				} else if (builtins[word]) {
					out += '<span class="ari-py-bi">' + pyEscape(word) + '</span>';
				} else {
					out += pyEscape(word);
				}
				i = k;
				continue;
			}

			if (/[0-9]/.test(ch)) {
				var n = i + 1;
				while (n < line.length && /[0-9._]/.test(line.charAt(n))) {
					n += 1;
				}
				out += '<span class="ari-py-num">' + pyEscape(line.slice(i, n)) + '</span>';
				i = n;
				continue;
			}

			out += pyEscape(ch);
			i += 1;
		}
		return out;
	}

	function buildAstrometricsExample(ctx) {
		var tab = String(ctx.tab || 'find-existing');
		var base = String(ctx.baseUrl || '');
		// Astrometrics endpoints are profile-agnostic; the page
		// reads/writes the shared on-disk DB at server-side.
		// Snippets use plain `requests` because ari_api does not
		// (yet) expose astrometrics methods.
		var introCommon = [
			'import requests',
			'',
			'# All astrometrics API calls require an authenticated',
			'# ARI session. Replace the cookie value below with',
			'# the value of the "session" cookie from your browser.',
			'SESSION = ' + quotePy('<paste your ari session cookie>'),
			'BASE = ' + quotePy(base),
			'COOKIES = {"session": SESSION}',
			'',
		];

		if (tab === 'find-existing') {
			return {
				title: 'Astrometrics API: find object in data portal',
				description: 'Find observations of a target across the profiles you have access to.',
				code: introCommon.concat([
					'r = requests.get(',
					'    BASE + "/api/astrometrics/find-object",',
					'    params={"name": "PROXIMA"},',
					'    cookies=COOKIES,',
					')',
					'r.raise_for_status()',
					'data = r.json()',
					'print("matches:", data.get("count"))',
					'for row in data.get("rows", []):',
					'    print(row)',
				]).join('\n'),
			};
		}

		if (tab === 'resolve-target') {
			return {
				title: 'Astrometrics API: resolve target by name',
				description: 'Look up an entry in the curated APERO astrometric database. The response includes the entry status (verified / pending / rejected).',
				code: introCommon.concat([
					'r = requests.get(',
					'    BASE + "/api/astrometrics/resolve-by-name",',
					'    params={"name": "PROXIMA"},',
					'    cookies=COOKIES,',
					')',
					'r.raise_for_status()',
					'payload = r.json()',
					'print("status:", payload.get("status"))',
					'print("apero_name:", payload.get("apero_name"))',
					'if payload.get("status") == "rejected":',
					'    print("WARNING: name is on the rejection list")',
				]).join('\n'),
			};
		}

		if (tab === 'astrom-db') {
			return {
				title: 'Astrometrics API: full database snapshot',
				description: 'Pull every row of the astrometric database (one summary row per APERO_NAME).',
				code: introCommon.concat([
					'r = requests.get(',
					'    BASE + "/api/astrometrics/list-all",',
					'    cookies=COOKIES,',
					')',
					'r.raise_for_status()',
					'data = r.json()',
					'print("entries:", data.get("count"))',
					'rows = data.get("rows", [])',
					'pending = [row for row in rows',
					'           if row.get("STATUS") == "pending"]',
					'print("pending:", len(pending))',
				]).join('\n'),
			};
		}

		if (tab === 'rejected') {
			return {
				title: 'Astrometrics API: rejected object names',
				description: 'List all entries on the rejection list, then add a new one.',
				code: introCommon.concat([
					'# List currently-rejected names',
					'r = requests.get(',
					'    BASE + "/api/astrometrics/list-rejected",',
					'    cookies=COOKIES,',
					')',
					'r.raise_for_status()',
					'print("rejected:", r.json().get("count"))',
					'',
					'# Add a new rejection (requires monitor perm)',
					'r = requests.post(',
					'    BASE + "/api/astrometrics/add-rejected",',
					'    json={',
					'        "apero_name": "MY_BAD_NAME",',
					'        "aliases": ["badname", "BAD_NAME"],',
					'        "notes": "added via API example",',
					'    },',
					'    cookies=COOKIES,',
					')',
					'print(r.status_code, r.json())',
				]).join('\n'),
			};
		}

		// fallback: list-all
		return {
			title: 'Astrometrics API',
			description: 'Generic astrometrics REST snippet.',
			code: introCommon.concat([
				'r = requests.get(',
				'    BASE + "/api/astrometrics/list-all",',
				'    cookies=COOKIES,',
				')',
				'print(r.status_code, r.json().get("count"))',
			]).join('\n'),
		};
	}

	function buildApiExample(meta) {
		var ctx = resolveApiContext(meta);
		if (!ctx) {
			return null;
		}
		if (ctx.pageType === 'object_table') return buildObjectTableExample(ctx);
		if (ctx.pageType === 'obs_table') return buildObsTableExample(ctx);
		if (ctx.pageType === 'basket') return buildBasketExample(ctx);
		if (ctx.pageType === 'object_page') return buildObjectPageExample(ctx);
		if (ctx.pageType === 'astrometrics') return buildAstrometricsExample(ctx);
		return null;
	}

	function createApiModal() {
		var existing = document.getElementById('ari-api-code-modal');
		if (existing) {
			return existing;
		}

		var modal = document.createElement('div');
		modal.id = 'ari-api-code-modal';
		modal.className = 'ari-api-modal';
		modal.style.display = 'none';
		modal.innerHTML = '' +
			'<div class="ari-api-modal__backdrop" data-api-close="1"></div>' +
			'<div class="ari-api-modal__panel" role="dialog" aria-modal="true" aria-labelledby="ari-api-modal-title">' +
			'  <div class="ari-api-modal__header">' +
			'    <h3 id="ari-api-modal-title">API Example</h3>' +
			'    <div class="ari-api-modal__actions">' +
			'      <button type="button" class="ari-btn ari-btn--sm ari-btn--secondary" id="ari-api-copy-btn">' +
			'        <i class="fa-solid fa-copy"></i> Copy' +
			'      </button>' +
			'      <button type="button" class="ari-btn ari-btn--sm ari-btn--secondary" data-api-close="1">' +
			'        <i class="fa-solid fa-xmark"></i>' +
			'      </button>' +
			'    </div>' +
			'  </div>' +
			'  <div class="ari-api-modal__body">' +
			'    <p class="ari-api-modal__note">Requires one-time <code>ari_api.configure(server=..., token=...)</code>. '
			+ '<a href="/docs/api?v=0.8.XXX#3-configuration" target="_blank" rel="noopener">See configuration docs</a>.</p>' +
			'    <p id="ari-api-modal-desc" class="ari-api-modal__desc"></p>' +
			'    <div class="ari-api-code-wrap">' +
			'      <ol id="ari-api-code-lines" class="ari-api-code-lines"></ol>' +
			'    </div>' +
			'  </div>' +
			'</div>';

		document.body.appendChild(modal);

		modal.addEventListener('click', function (ev) {
			var t = ev.target;
			if (!(t instanceof Element)) return;
			if (t.getAttribute('data-api-close') === '1') {
				modal.style.display = 'none';
				document.body.classList.remove('ari-modal-open');
			}
		});

		document.addEventListener('keydown', function (ev) {
			if (ev.key === 'Escape' && modal.style.display !== 'none') {
				modal.style.display = 'none';
				document.body.classList.remove('ari-modal-open');
			}
		});

		return modal;
	}

	function showApiModal(example) {
		if (!example) return;
		var modal = createApiModal();
		var titleEl = modal.querySelector('#ari-api-modal-title');
		var descEl = modal.querySelector('#ari-api-modal-desc');
		var listEl = modal.querySelector('#ari-api-code-lines');
		var copyBtn = modal.querySelector('#ari-api-copy-btn');
		if (!titleEl || !descEl || !listEl || !copyBtn) return;

		titleEl.textContent = String(example.title || 'API Example');
		descEl.textContent = String(example.description || '');

		var code = String(example.code || '');
		var lines = code.replace(/\n+$/g, '').split('\n');
		listEl.innerHTML = lines.map(function (line) {
			return '<li><span>'
				+ highlightPythonLine(String(line))
				+ '</span></li>';
		}).join('');

		copyBtn.onclick = function () {
			var labelBefore = copyBtn.innerHTML;
			navigator.clipboard.writeText(code).then(function () {
				copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied';
				window.setTimeout(function () {
					copyBtn.innerHTML = labelBefore;
				}, 1200);
			}).catch(function () {
				window.alert('Could not copy to clipboard.');
			});
		};

		modal.style.display = '';
		document.body.classList.add('ari-modal-open');
	}

	function createPageIssueModal() {
		var existing = document.getElementById('ari-page-issue-modal');
		if (existing) return existing;
		var modal = document.createElement('div');
		modal.id = 'ari-page-issue-modal';
		modal.className = 'ari-api-modal';
		modal.style.display = 'none';
		modal.innerHTML = '' +
			'<div class="ari-api-modal__backdrop"' +
			' data-issue-close="1"></div>' +
			'<div class="ari-api-modal__panel" role="dialog"' +
			' aria-modal="true"' +
			' aria-labelledby="ari-page-issue-modal-title">' +
			'  <div class="ari-api-modal__header">' +
			'    <h3 id="ari-page-issue-modal-title">' +
			'Report an issue with this page</h3>' +
			'    <div class="ari-api-modal__actions">' +
			'      <button type="button"' +
			' class="ari-btn ari-btn--sm ari-btn--secondary"' +
			' data-issue-close="1">' +
			'<i class="fa-solid fa-xmark"></i></button>' +
			'    </div>' +
			'  </div>' +
			'  <div class="ari-api-modal__body">' +
			'    <p class="ari-api-modal__note">This issue will be' +
			' filed against the current page' +
			' (<code id="ari-page-issue-url"></code>) and visible' +
			' to monitors.</p>' +
			'    <label for="ari-page-issue-title"' +
			' class="ari-api-modal__desc">Title</label>' +
			'    <input id="ari-page-issue-title" type="text"' +
			' style="width:100%;padding:0.4rem 0.55rem;margin:' +
			'0.25rem 0 0.7rem;border:1px solid rgba(0,0,0,0.18);' +
			'border-radius:6px;" placeholder="Brief summary"' +
			' />' +
			'    <label for="ari-page-issue-reason"' +
			' class="ari-api-modal__desc">Description</label>' +
			'    <textarea id="ari-page-issue-reason" rows="5"' +
			' style="width:100%;padding:0.4rem 0.55rem;margin:' +
			'0.25rem 0 0.7rem;border:1px solid rgba(0,0,0,0.18);' +
			'border-radius:6px;font:inherit;"' +
			' placeholder="Describe the problem (optional if a' +
			' title is given)"></textarea>' +
			'    <div id="ari-page-issue-status"' +
			' style="min-height:1.2em;font-size:0.85rem;' +
			'color:var(--ari-text-muted);"></div>' +
			'    <div style="display:flex;gap:0.5rem;' +
			'justify-content:flex-end;margin-top:0.6rem;">' +
			'      <button type="button"' +
			' class="ari-btn ari-btn--sm ari-btn--secondary"' +
			' data-issue-close="1">Cancel</button>' +
			'      <button type="button"' +
			' class="ari-btn ari-btn--sm ari-btn--primary"' +
			' id="ari-page-issue-submit">' +
			'<i class="fa-solid fa-paper-plane"></i>' +
			' Submit</button>' +
			'    </div>' +
			'  </div>' +
			'</div>';
		document.body.appendChild(modal);
		modal.addEventListener('click', function (ev) {
			var t = ev.target;
			if (!(t instanceof Element)) return;
			if (t.getAttribute('data-issue-close') === '1') {
				modal.style.display = 'none';
				document.body.classList.remove('ari-modal-open');
			}
		});
		document.addEventListener('keydown', function (ev) {
			if (ev.key === 'Escape'
					&& modal.style.display !== 'none') {
				modal.style.display = 'none';
				document.body.classList.remove('ari-modal-open');
			}
		});
		return modal;
	}

	function showPageIssueModal(meta) {
		var modal = createPageIssueModal();
		var urlEl = modal.querySelector('#ari-page-issue-url');
		var titleEl = modal.querySelector('#ari-page-issue-title');
		var reasonEl = modal.querySelector(
			'#ari-page-issue-reason');
		var statusEl = modal.querySelector(
			'#ari-page-issue-status');
		var submitBtn = modal.querySelector(
			'#ari-page-issue-submit');
		var pageLabel = normalizePageLabel(meta);
		var url = window.location.pathname + window.location.search;
		urlEl.textContent = url;
		titleEl.value = '';
		reasonEl.value = '';
		statusEl.textContent = '';
		titleEl.placeholder = 'Issue with: ' + pageLabel;
		submitBtn.disabled = false;
		modal.style.display = '';
		document.body.classList.add('ari-modal-open');
		window.setTimeout(function () { titleEl.focus(); }, 30);
		submitBtn.onclick = async function () {
			var title = String(titleEl.value || '').trim();
			var reason = String(reasonEl.value || '').trim();
			if (!title && !reason) {
				statusEl.textContent =
					'Please enter a title or a description.';
				return;
			}
			submitBtn.disabled = true;
			statusEl.textContent = 'Submitting…';
			try {
				var resp = await fetch('/api/issues/create', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						kind: 'ari',
						type: 'page',
						title: title || ('Issue with: '
							+ pageLabel),
						reason: reason || title
							|| ('Issue with: ' + pageLabel),
						origin_url: url,
						visibility: 'monitor'
					})
				});
				var data = await resp.json();
				if (!data.success) {
					statusEl.textContent = 'Error: '
						+ (data.error || 'unknown');
					submitBtn.disabled = false;
					return;
				}
				statusEl.textContent =
					'Submitted (issue #' + data.issue.id + ').';
				window.setTimeout(function () {
					modal.style.display = 'none';
					document.body.classList.remove(
						'ari-modal-open');
				}, 900);
			} catch (err) {
				statusEl.textContent = 'Error: '
					+ (err.message || 'network');
				submitBtn.disabled = false;
			}
		};
	}

	document.addEventListener('DOMContentLoaded', async function () {
		var meta = window.ARI_PAGE_META || null;
		var enablePins = shouldEnablePins(meta);
		var enableApi = shouldEnableApi(meta);
		var enableFavourite = shouldEnableFavourite(meta);
		var enableIssue = shouldEnableIssue(meta);
		if (!enablePins && !enableApi && !enableFavourite
				&& !enableIssue) {
			return;
		}

		var mainContent = document.querySelector('.ari-main');
		if (!mainContent) {
			return;
		}

		if (mainContent.querySelector('.ari-page-fab-group')) {
			return;
		}

		var group = document.createElement('div');
		group.className = 'ari-page-fab-group';
		mainContent.appendChild(group);

		if (enableApi) {
			var apiBtn = document.createElement('button');
			apiBtn.type = 'button';
			apiBtn.className = 'ari-page-pin-fab ari-page-api-fab';
			apiBtn.title = 'API examples for this page';
			apiBtn.setAttribute('aria-label', apiBtn.title);
			apiBtn.innerHTML = iconSpan('<i class="fa-solid fa-code"></i>');
			apiBtn.addEventListener('click', function () {
				showApiModal(buildApiExample(meta));
			});
			group.appendChild(apiBtn);
		}

		if (enableIssue) {
			var issueBtn = document.createElement('button');
			issueBtn.type = 'button';
			issueBtn.className =
				'ari-page-pin-fab ari-page-issue-fab';
			issueBtn.title = 'Report an issue with this page';
			issueBtn.setAttribute('aria-label', issueBtn.title);
			issueBtn.innerHTML = iconSpan(
				'<i class="fa-solid fa-circle-exclamation"></i>');
			issueBtn.addEventListener('click', function () {
				showPageIssueModal(meta);
			});
			group.appendChild(issueBtn);
		}

		if (enableFavourite) {
			var favCfg = window.ARI_OBJECT_PAGE || {};
			var favBtn = document.createElement('button');
			favBtn.type = 'button';
			favBtn.className = 'ari-page-pin-fab ari-page-favourite-fab';
			group.appendChild(favBtn);

			try {
				var isFavourite = await fetchFavouriteState(favCfg);
				renderFavouriteState(favBtn, isFavourite);
			} catch (err) {
				favBtn.remove();
			}

			var favBusy = false;
			favBtn.addEventListener('click', async function () {
				if (favBusy) {
					return;
				}
				favBusy = true;
				favBtn.disabled = true;
				try {
					var state = await toggleFavourite(favCfg);
					renderFavouriteState(favBtn, state);
				} catch (err) {
					window.alert(err.message || 'Could not update favourites.');
				} finally {
					favBusy = false;
					favBtn.disabled = false;
				}
			});
		}

		if (!enablePins) {
			return;
		}

		var button = document.createElement('button');
		button.type = 'button';
		button.className = 'ari-page-pin-fab';
		group.appendChild(button);

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
			if (!group.querySelector('.ari-page-pin-fab')) {
				group.remove();
			}
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

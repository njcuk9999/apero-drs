const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname,
  '../apero_ri/static/js/user_portal_users.js'), 'utf8');

async function render(awards) {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, {
      innerHTML: '', value: '', textContent: '',
      addEventListener() {}, appendChild() {}
    });
    return elements.get(id);
  }
  const user = {
    username: 'reader', first_names: '<script>bad()</script>',
    groups: ['general'], awards, can_view_contact: false,
    email: 'private@example.test'
  };
  const context = {
    window: { USER_DOWNLOAD_AWARD_LABELS: {
      bytes: 'Volume <test>', files: 'Fichiers',
      gold: 'Or', silver: 'Argent', bronze: 'Bronze'
    } },
    document: {
      getElementById: element, createElement: () => element(Symbol()),
      addEventListener() {}
    },
    fetch: async () => ({ json: async () => ({
      success: true, users: [user], all_groups: ['general'], instruments: []
    }) })
  };
  vm.runInNewContext(source, context);
  await new Promise(resolve => setImmediate(resolve));
  return element('upm-users-grid').innerHTML;
}

async function main() {
  const html = await render({
    download_bytes: 4096, download_files: 8,
    download_medals: { bytes: 'gold', files: 'silver' },
    instrument_medals: { SPIROU: 'bronze' },
    service_medal: 'silver', total_hours: 100,
    issues_medal: 'bronze', issues_resolved: 250
  });
  assert.match(html, /upu-medal--gold/);
  assert.match(html, /Volume &lt;test&gt;: 4096 B \(Or\)/);
  assert.match(html, /Fichiers: 8 \(Argent\)/);
  assert.match(html, /aria-label="Volume &lt;test&gt;/);
  assert.match(html, /SPIROU top monitor/);
  assert.match(html, /Service award/);
  assert.match(html, /Issue resolution award/);
  assert.doesNotMatch(html, /private@example\.test|<script>bad/);
  const zero = await render({
    download_bytes: 0, download_files: 0,
    download_medals: { bytes: null, files: null }
  });
  assert.doesNotMatch(zero, /upu-user-card__awards|fa-medal/);
  assert.doesNotMatch(await render({}), /fa-medal/);
  const filesOnly = await render({
    download_files: 2, download_medals: { bytes: null, files: 'bronze' }
  });
  assert.match(filesOnly, /Fichiers: 2 \(Bronze\)/);
  assert.doesNotMatch(filesOnly, /Volume &lt;test&gt;/);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
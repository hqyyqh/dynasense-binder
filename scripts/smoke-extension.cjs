// Run inside the built Linux image; UI acceptance is recorded separately.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const folder = path.join(os.homedir(), '.local/share/code-server/extensions');
const matches = fs.readdirSync(folder).filter(name => name.startsWith('hqyyqh.dynasense-'));
assert.equal(matches.length, 1, 'Expected one installed DynaSense package');
const extension = path.join(folder, matches[0]);
const metadata = JSON.parse(fs.readFileSync(path.join(extension, 'package.json')));
assert.equal(metadata.publisher, 'hqyyqh');
assert.equal(metadata.name, 'dynasense');
const lock = JSON.parse(fs.readFileSync('runtime-assets.json'));
assert.equal(metadata.version, lock.extension.version);
const semver = require(path.join(extension, 'node_modules/semver'));
const host = require('node:child_process').execFileSync('code-server', ['--version'], { encoding: 'utf8' });
const hostVersion = host.match(/Code ([0-9.]+)/)?.[1];
assert(hostVersion && semver.satisfies(hostVersion, metadata.engines.vscode), 'Host must satisfy the VSIX engine');
const sqlite = require(path.join(extension, 'node_modules/@vscode/sqlite3'));
const database = new sqlite.Database(':memory:');
database.get('SELECT sqlite_version() AS version, 1 + 1 AS result', (error, row) => {
  if (error) throw error;
  assert.equal(row.result, 2);
  console.log(JSON.stringify({ extension: metadata.version, node: process.version, sqlite: row.version, query: 'passed' }));
  database.close();
});
require('node:child_process').execFileSync(process.execPath, [
  'scripts/profile-manual.cjs', path.join(extension, 'out'), 'manual-pack',
  path.join(os.tmpdir(), 'dynasense-manual-profile.json'),
], { stdio: 'inherit' });

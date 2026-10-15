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
const sqlite = require(path.join(extension, 'node_modules/@vscode/sqlite3'));
const database = new sqlite.Database(':memory:');
database.get('SELECT sqlite_version() AS version, 1 + 1 AS result', (error, row) => {
  if (error) throw error;
  assert.equal(row.result, 2);
  console.log(JSON.stringify({ extension: metadata.version, node: process.version, sqlite: row.version, query: 'passed' }));
  database.close();
});

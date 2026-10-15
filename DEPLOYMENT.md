# Binder validation environment

Release monitoring is defined in `.github/workflows/check-plugin-release.yml`.
It checks daily at 09:23 Asia/Shanghai and can be run manually. `release-policy.json`
uses `github-release`: the original latest stable Linux x64 VSIX is the demo baseline.
A new verified release creates a candidate branch and PR and explicitly starts the
runtime build. No update creates no commit. Promotion follows actual bilingual
operation and startup acceptance; running visitor sessions are not upgraded.

This directory is the deployment recipe for https://github.com/hqyyqh/dynasense-binder.
The homepage still opens the existing local experience until online acceptance passes.

## Assembly

Use an isolated staging directory for a public deployment. Copy this recipe, its
scripts and the complete `demo/` directory. `runtime-assets.json` pins the exact
Linux x64 VSIX and manual archive URLs and SHA-256 hashes. `fetch-assets.py` downloads
and verifies them before installation. Keep source snapshots and package evidence
in the internal acceptance record.

The full manual measurement uses `manual-pack/` with its original manifest,
documents, indexes, images and PDFs. PDF opening and page navigation are excluded
from this round. Do not substitute the earlier English-only website reference pack.
Manual assets are not committed to Git. The owner authorized public distribution
on 2026-10-15. The full pack is available as the immutable manual-full-20261015
release asset in the deployment repository.

After verifying the downloaded archive, `fetch-assets.py` writes `assets/manifest.json`,
mapping each staged artifact's repository-relative path to its SHA-256.
`postBuild` checks these bytes, installs the extension and sets the manual path.
Missing artifacts stop the build. It does not download an older release silently.

Keep `environment.yml`, `postBuild` and `start` at the root of the assembled Binder
repository. Commit shell files with LF line endings and executable mode. The
environment versions were checked against conda-forge/PyPI on 2026-10-15.
The launch targets are `?urlpath=vscode-zh/` and `?urlpath=vscode-en/`.
Both use the same installed extension, manual pack and editable case files.
The locale profiles set both the host display language and `lsdyna.language`.
Image construction indexes the installed Chinese translation files for both profiles.
Workspace trust prompts are disabled only in these disposable demo profiles, as
requested by the owner. Visitors can edit their private session's example files.
The dedicated environment still requires end-to-end acceptance before homepage use.

## Measurement

Run the memory sampler in the Binder terminal before completing the operation list:

```sh
python scripts/sample-memory.py measurements/session.jsonl --seconds 600
```

Use a second terminal for editing operations. Record timestamps for editor readiness,
extension activation, include indexing, card manager opening, manual opening,
English/Chinese/bilingual reading and searches. Record browser launch time separately;
the sampler starts after entering the environment and cannot measure launch latency.
The Linux sampler records the visible container cgroup, not the browser's RAM.
Its peak counter can include earlier build/startup operations; compare current values
and record the cgroup scope. Test a cached launch separately from a first image build.

The source-side manual profile can be repeated with Node:

```sh
node profile-manual.cjs /path/to/extension/out /path/to/manual-pack report.json
```

Copy `scripts/profile-manual.cjs` from the website repository when using this command.
It invokes the real compiled repository, opens both chapter texts, loads the sentence
map, and searches both languages. It measures one standalone Node process, not an
installed extension or the full Binder session. It never opens a PDF.

## Acceptance

- Plugin activation, actual SQLite loading and a database-backed query.
- Keyword completion, field navigation/editing, formatting and undo.
- Include navigation, keyword indexing, definitions and entity references.
- Card manager application, document changes, save and undo.
- Manual chapter loading, images/formulas, language switching and both searches.
- Browser shortcut/focus behavior and actual Chinese/English interface review.
- Complete-session memory and end-to-end startup time.
- A second independent session starts with the original example.

Do not replace the homepage link until these are recorded against the Linux package.

References: [VS Code on Binder](https://github.com/betatim/vscode-binder),
[repo2docker actions](https://repo2docker.readthedocs.io/en/latest/configuration/actions/).

'use strict';
// Runs the actual compiled repository in a fresh process; no PDF is opened.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { performance } = require('node:perf_hooks');
const { createHash } = require('node:crypto');
const [compiledRoot, packRoot, output] = process.argv.slice(2);
assert(compiledRoot && packRoot && output, 'Usage: node profile-manual.cjs <compiled-root> <manual-pack> <report.json>');
const modulePath = path.resolve(compiledRoot, 'manual/ManualIndexRepository.js');
const { ManualIndexRepository } = require(modulePath);
const repo = new ManualIndexRepository(path.resolve(packRoot));
const phases = [];
function measure(name, action) {
  const started = performance.now();
  const result = action();
  phases.push({ name, milliseconds: performance.now() - started, memory: process.memoryUsage(),
    processPeakRssKiB: process.resourceUsage().maxRSS, result });
}
measure('baseline', () => repo.getCapabilities());
measure('navigation', () => {
  repo.loadNavigation();
  assert(repo.sectionCount() > 0);
  return { keywords: repo.keywordCount(), sections: repo.sectionCount() };
});
const section = repo.listSections().find(s => s.titleEn.includes('DEFINE_CURVE') && s.pathEn && s.pathZh);
assert(section, 'A bilingual DEFINE_CURVE chapter is required');
const chunks = [];
measure('read-chapter-en-zh', () => {
  for (const relative of [section.pathEn, section.pathZh]) {
    const absolute = path.resolve(packRoot, relative);
    assert(absolute.startsWith(path.resolve(packRoot) + path.sep));
    chunks.push(fs.readFileSync(absolute, 'utf8'));
  }
  assert(chunks.every(text => text.length > 0));
  return { characters: chunks.map(text => text.length) };
});
measure('sentence-map-prewarm', () => {
  repo.ensureSentencesLoaded();
  assert(repo.sentenceCount() > 0);
  return { sentences: repo.sentenceCount(), chapterPairs: repo.getSectionSentences(section.manualId, section.sectionId).length };
});
measure('search-en', () => {
  const results = repo.search('curve', 'en', 20, 'fulltext');
  assert(results.length > 0);
  return { results: results.length };
});
measure('search-zh', () => {
  const results = repo.search('曲线', 'zh', 20, 'fulltext');
  assert(results.length > 0);
  return { results: results.length };
});
measure('warm-search-both', () => ({ results: repo.search('DEFINE_CURVE', 'both', 20).length }));
const report = { measuredAt: new Date().toISOString(), node: process.version, platform: process.platform,
  architecture: process.arch, scope: 'Actual manual repository in standalone Node; not Binder, VS Code, Webview or container memory',
  pdfOpened: false, moduleSha256: createHash('sha256').update(fs.readFileSync(modulePath)).digest('hex'),
  manualManifestSha256: createHash('sha256').update(fs.readFileSync(path.join(packRoot, 'manifest.json'))).digest('hex'), phases };
fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));

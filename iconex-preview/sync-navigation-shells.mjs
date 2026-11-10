// Run after editing index.html: node iconex-preview/sync-navigation-shells.mjs
import { readFile, mkdir, writeFile } from 'node:fs/promises';
const root = new URL('./', import.meta.url);
const html = await readFile(new URL('index.html', root), 'utf8');
const paths = ['about','events/upcoming-events','events/all-events','global-presence','gallery','career','contact'];
for (const path of paths) {
  await mkdir(new URL(path + '/', root), {recursive:true});
  await writeFile(new URL(path + '/index.html', root), html);
}
console.log(`Updated ${paths.length} static navigation shells.`);

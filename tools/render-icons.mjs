import { readFile, writeFile } from 'node:fs/promises';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import * as icons from 'lucide-react';

const pages = ['index.html', '404.html', 'beta/index.html', 'privacy/index.html', 'support/index.html', 'terms/index.html'];
const check = process.argv.includes('--check');

for (const page of pages) {
  const url = new URL(`../${page}`, import.meta.url);
  const html = await readFile(url, 'utf8');
  const rendered = html.replace(/<svg\b([^>]*)>[\s\S]*?<\/svg>/g, (svg, attributes) => {
    const name = attributes.match(/\bdata-lucide="([^"]+)"/)?.[1];
    if (!name) return svg;
    if (!Object.hasOwn(icons, name) || !/^[A-Z]/.test(name)) {
      throw new Error(`Unknown Lucide icon "${name}" in ${page}`);
    }
    const className = attributes.match(/\bclass="([^"]*)"/)?.[1]
      .split(/\s+/).filter((name) => name && !name.startsWith('lucide')).join(' ');
    return renderToStaticMarkup(createElement(icons[name], {
      'data-lucide': name,
      width: attributes.match(/(?:^|\s)width="([^"]+)"/)?.[1] || 24,
      height: attributes.match(/(?:^|\s)height="([^"]+)"/)?.[1] || 24,
      className: className || undefined,
      'aria-hidden': 'true',
      focusable: 'false',
    }));
  });
  if (rendered !== html) {
    if (check) throw new Error(`Stale icons in ${page}; run npm run icons`);
    await writeFile(url, rendered);
  }
}
console.log(check ? 'All Lucide icons are up to date.' : 'Lucide icons rendered into static HTML.');

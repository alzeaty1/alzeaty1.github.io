import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

function escapeXml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export async function GET({ site }: APIContext) {
  if (!site) throw new Error('Astro site URL must be configured to generate the sitemap.');

  const writeups = await getCollection('writeups');
  const paths = [
    '/',
    '/about',
    '/projects/',
    '/writeups/',
    ...writeups.map((entry) => `/writeups/${entry.id}/`),
  ];
  const urls = paths
    .map((path) => `  <url><loc>${escapeXml(new URL(path, site).toString())}</loc></url>`)
    .join('\n');

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>`,
    { headers: { 'Content-Type': 'application/xml; charset=utf-8' } },
  );
}

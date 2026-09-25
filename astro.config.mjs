// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// Static site for GitHub Pages. The repo will be the user/org page, so base is root.
export default defineConfig({
  site: 'https://alzeaty1.github.io',
  base: '/',
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [mdx()],
});

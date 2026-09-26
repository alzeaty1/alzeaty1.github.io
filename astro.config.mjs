// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import rehypeScrollWrap from './src/lib/rehypeScrollWrap.mjs';

/**
 * Shiki theme built from the Deep Sea palette so highlighted code sits on
 * --surface with --rule borders and --text base colour, instead of Astro's
 * default github-dark (#24292e). Token colours are chosen for AA contrast
 * on #1d2d44.
 */
const deepSea = {
  name: 'deep-sea',
  type: 'dark',
  colors: {
    'editor.background': '#1d2d44',
    'editor.foreground': '#f0ebd8',
  },
  settings: [
    {
      settings: {
        background: '#1d2d44',
        foreground: '#f0ebd8',
      },
    },
    {
      scope: ['comment', 'punctuation.definition.comment'],
      settings: { foreground: '#93a4b6', fontStyle: 'italic' },
    },
    {
      scope: ['string', 'string.quoted', 'constant.other.symbol'],
      settings: { foreground: '#8fd0b4' },
    },
    {
      scope: ['constant.numeric', 'constant.language', 'variable.language'],
      settings: { foreground: '#e0a86b' },
    },
    {
      scope: ['keyword', 'storage', 'storage.type', 'keyword.control'],
      settings: { foreground: '#e06b3f' },
    },
    {
      scope: ['entity.name.function', 'support.function', 'meta.function-call'],
      settings: { foreground: '#7fb2e5' },
    },
    {
      scope: ['entity.name.tag', 'entity.name.type', 'support.type', 'support.class'],
      settings: { foreground: '#7fd4c1' },
    },
    {
      scope: ['variable', 'variable.other', 'meta.object-literal.key'],
      settings: { foreground: '#f0ebd8' },
    },
    {
      scope: ['entity.name.tag', 'punctuation.definition.tag'],
      settings: { foreground: '#6a839f' },
    },
    {
      scope: ['keyword.operator', 'punctuation.separator', 'punctuation.accessor'],
      settings: { foreground: '#93a4b6' },
    },
    {
      scope: ['invalid', 'invalid.illegal'],
      settings: { foreground: '#e06b3f' },
    },
  ],
};

// Static site for GitHub Pages. The repo will be the user/org page, so base is root.
export default defineConfig({
  site: 'https://alzeaty1.github.io',
  base: '/',
  output: 'static',
  trailingSlash: 'ignore',
  integrations: [
    mdx({
      rehypePlugins: [rehypeScrollWrap],
    }),
  ],
  markdown: {
    rehypePlugins: [rehypeScrollWrap],
    shikiConfig: {
      theme: deepSea,
      wrap: false,
    },
  },
});

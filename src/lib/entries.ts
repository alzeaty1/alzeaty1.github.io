import { getCollection, type CollectionEntry } from 'astro:content';

export type Writeup = CollectionEntry<'writeups'>;

/**
 * Load the collection once and split it the way the site navigates it:
 * standalone writeups (which get index entries) and appendices (which are
 * linked from their parent writeup instead).
 */
export async function loadWriteups() {
  const all = await getCollection('writeups');
  const standalone = all
    .filter((entry) => entry.data.appendix !== true)
    .sort((a, b) => a.id.localeCompare(b.id));
  const appendices = all.filter((entry) => entry.data.appendix === true);
  return { all, standalone, appendices };
}

export function appendixParentSlug(appendix: Writeup) {
  // parent is authored as "/sqli"
  return (appendix.data.parent ?? '').replace(/^\//, '');
}

export function appendicesFor(slug: string, appendices: Writeup[]) {
  return appendices.filter((a) => appendixParentSlug(a) === slug);
}

/** Short human label for a difficulty string, used in listings. */
export function difficultyLabel(entry: Writeup) {
  return entry.data.difficulty.toLowerCase();
}

/** Which downloadable helper scripts belong to a given writeup slug. */
const SCRIPT_LINKS: Record<string, { href: string; note: string }[]> = {
  beachbar: [
    { href: '/scripts/beachbar_rce.py', note: 'PyYAML deserialization RCE payload generator' },
  ],
  sqli: [
    { href: '/scripts/boolean_blind_enum.py', note: 'boolean blind, single character' },
    { href: '/scripts/time_based_enum.py', note: 'time-based blind against the timing oracle' },
  ],
  'packed-light': [
    { href: '/scripts/decode_cookies_teaching_EN.py', note: 'cookie decoder, annotated for teaching' },
  ],
};

export function scriptsFor(slug: string) {
  return SCRIPT_LINKS[slug] ?? [];
}

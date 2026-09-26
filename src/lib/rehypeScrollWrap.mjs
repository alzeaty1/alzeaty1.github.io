// @ts-check
/**
 * Rehype plugin: wrap wide content in a horizontal scroll container.
 *
 * Two things in a writeup can be wider than a 375px viewport and have no
 * legal way to reflow (a payload must stay byte-for-byte identical, and a
 * word-break would change how a request reads):
 *
 *   - <table>            wide reference tables
 *   - bare inline <code> long unbreakable tokens (headers, payloads, paths)
 *
 * Both get wrapped in a .prose__scroll box. CSS gives that box
 * `overflow-x: auto`, so the overflow is contained and the page itself never
 * scrolls sideways. Nothing about the content changes: no text is touched, no
 * whitespace is touched, and the code keeps white-space: pre.
 *
 * The wrapper is only *capable* of scrolling. A client-side pass in
 * [slug].astro then adds tabindex/role and the reader hint, but only to the
 * boxes that actually overflow - so short code spans never become tab stops.
 *
 * Note the shape: this is an attacher, not a transformer. Unified calls it
 * once with no arguments to obtain the real transformer, so a plugin written
 * as `(tree) => {...}` receives `undefined` and silently does nothing.
 */
export default function rehypeScrollWrap() {
  return (/** @type {any} */ tree) => {
    walk(tree, false);
  };
}

/** @param {any} node */
function isElement(node) {
  return node && node.type === 'element';
}

/**
 * @param {any} node
 * @param {boolean} inPre
 */
function walk(node, inPre) {
  // MDX trees can carry null / non-element nodes; skip anything that is not
  // a container we own rather than walking into it.
  if (!node || typeof node !== 'object') return;
  if (node.type !== 'root' && !isElement(node)) return;
  if (!Array.isArray(node.children)) return;

  const tag = isElement(node) ? node.tagName : '';
  const nowInPre = inPre || tag === 'pre';

  /** @type {any[]} */
  const next = [];
  for (const child of node.children) {
    // Descend first, so a <code> sitting inside a table cell is wrapped too.
    walk(child, nowInPre);

    if (isElement(child) && !nowInPre) {
      if (child.tagName === 'table') {
        next.push(wrap('div', ['prose__scroll', 'prose__scroll--table'], child));
        continue;
      }
      if (child.tagName === 'code') {
        next.push(wrap('span', ['prose__scroll', 'prose__scroll--code'], child));
        continue;
      }
    }
    next.push(child);
  }
  node.children = next;
}

/**
 * @param {string} tag
 * @param {string[]} className
 * @param {any} child
 */
function wrap(tag, className, child) {
  return {
    type: 'element',
    tagName: tag,
    properties: { className },
    children: [child],
  };
}

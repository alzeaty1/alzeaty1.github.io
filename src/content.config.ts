import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Writeups.
 *
 * The schema mirrors the frontmatter that is actually present in the ten
 * files under src/content/writeups/ — nothing is invented, nothing is required
 * that the files do not carry. Every key below is optional except `title`,
 * `room`, `difficulty`, `platform` and `spoilerFree`, which are present in all
 * ten. `vulnClass` is present in all ten as well but is coerced to a string so
 * that an unwrapped scalar in YAML cannot fail validation.
 */
const writeups = defineCollection({
  loader: glob({ base: './src/content/writeups', pattern: '**/*.mdx' }),
  schema: z.object({
    title: z.string(),
    room: z.string(),
    difficulty: z.string(),
    platform: z.string().optional(),
    vulnClass: z.string().optional(),
    spoilerFree: z.boolean().optional(),
    // present only on sqli.mdx
    dateSolved: z.coerce.date().optional(),
    // present only on sqli-quick-reference.mdx
    appendix: z.boolean().optional(),
    parent: z.string().optional(),
  }),
});

export const collections = { writeups };

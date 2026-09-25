import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    modDate: z.coerce.date().optional(),
    author: z.string().default('MineBed Team'),
    cover: z.string().optional(),
    tags: z.array(z.string()).default([]),
    category: z.string().default('news'),
    featured: z.boolean().default(false),
    draft: z.boolean().default(false),
    readingTime: z.number().optional(),
  }),
});

const wiki = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/wiki' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    modDate: z.coerce.date().optional(),
    author: z.string().default('MineBed Team'),
    cover: z.string().optional(),
    tags: z.array(z.string()).default([]),
    topic: z.string(),
    mcVersion: z.string().default('1.21'),
    draft: z.boolean().default(false),
  }),
});

const tutorials = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/tutorials' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    modDate: z.coerce.date().optional(),
    author: z.string().default('MineBed Team'),
    cover: z.string().optional(),
    tags: z.array(z.string()).default([]),
    difficulty: z.enum(['beginner', 'intermediate', 'advanced']).default('beginner'),
    duration: z.number().default(10),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog, wiki, tutorials };

import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'
import { z } from 'astro/zod'

const lessons = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/lessons' }),
  schema: z.object({
    title: z.string(),
    week: z.number().int().min(1).max(18),
    description: z.string(),
    goals: z.array(z.string()).optional(),
  }),
})

const docs = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/docs' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
  }),
})

const glossary = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/glossary' }),
  schema: z.object({
    term: z.string(),
    definition: z.string(),
    category: z.enum(['網路', '資料庫', '資訊安全', 'DevOps', '寫作', '工具']).optional(),
    first: z.number().int().min(1).max(18).optional(),
  }),
})

export const collections = { lessons, docs, glossary }

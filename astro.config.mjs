// @ts-check

import mdx from '@astrojs/mdx'

import react from '@astrojs/react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'astro/config'
import icon from 'astro-icon'

// https://astro.build/config
export default defineConfig({
  site: 'https://gloomcheng.github.io',
  base: '/115-backend',
  integrations: [icon({ include: { lucide: ['menu', 'x'] } }), react(), mdx()],

  vite: {
    plugins: [tailwindcss()],
  },
})

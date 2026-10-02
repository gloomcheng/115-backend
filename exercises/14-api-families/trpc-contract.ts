// Lesson 14 — the tRPC contract. A contract file, not a running service.
//
// The difference from gRPC is where the contract lives. gRPC states it in
// a .proto file that a code generator reads. tRPC states it in a
// TypeScript router, and the client's type is inferred from it, so the
// contract is checked by the type checker rather than by a generator.
//
// Nothing in this directory runs it. Read it next to notes.proto and
// compare which errors each one can catch, and when.

import { initTRPC } from '@trpc/server'
import { z } from 'zod'

const t = initTRPC.create()

export const notesRouter = t.router({
  // Each procedure states its input with zod, and its output with a type.
  // Ask for a field the server does not return and the client's type says so
  // before a single request is sent.
  list: t.procedure.input(t.void()).output(
    t.array(
      z.object({
        name: z.string(),
        title: z.string(),
        tags: z.array(z.string()),
      })
    )
  ),

  get: t.procedure
    // The input is validated on the server before the handler runs.
    .input(z.object({ name: z.string() }))
    .output(
      z.object({
        name: z.string(),
        title: z.string(),
        tags: z.array(z.string()),
      })
    ),
})

export type NotesRouter = typeof notesRouter

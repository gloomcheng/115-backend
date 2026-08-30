import { useState } from 'react'
import { interactiveCopy } from '../../data/interactive-copy'

type Method = keyof typeof interactiveCopy.idempotency.methods

export default function IdempotentDemo() {
  const copy = interactiveCopy.idempotency
  const [method, setMethod] = useState<Method>('GET')
  const [runs, setRuns] = useState(0)
  const current = copy.methods[method]

  const response =
    runs === 0 ? copy.initialState : runs === 1 ? current.firstResponse : current.repeatResponse
  const state =
    runs === 0
      ? copy.initialState
      : method === 'POST'
        ? `${current.firstState}：${runs}`
        : runs === 1
          ? current.firstState
          : current.repeatState

  return (
    <section className="my-10 border-y-2 border-[#075486] bg-[#fff0bf] px-5 py-7 text-[#075486] not-prose sm:px-7">
      <p className="font-mono text-xs font-bold tracking-[.16em] text-[#ef795e]">{copy.eyebrow}</p>
      <h3 className="mt-2 max-w-3xl text-2xl font-bold tracking-[-.03em] sm:text-3xl">
        {copy.title}
      </h3>
      <p className="mt-3 max-w-3xl text-base leading-7 text-[#274f67]">{copy.description}</p>

      <div className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {(Object.keys(copy.methods) as Method[]).map((item) => (
          <button
            key={item}
            type="button"
            aria-pressed={method === item}
            onClick={() => {
              setMethod(item)
              setRuns(0)
            }}
            className={`rounded-[4px] border-2 border-[#075486] px-3 py-2 font-mono text-sm font-bold transition-colors ${
              method === item
                ? 'bg-[#075486] text-[#fffaf0]'
                : 'bg-[#fffaf0] text-[#075486] hover:bg-[#b8d8e8]'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-[minmax(0,1fr)_48px_minmax(0,1fr)] md:items-stretch">
        <div className="min-w-0 rounded-[4px] border-2 border-[#075486] bg-[#fffaf0] p-5">
          <p className="font-mono text-xs font-bold tracking-[.12em] text-[#ef795e]">
            {copy.requestLabel}
          </p>
          <p className="mt-3 overflow-x-auto whitespace-nowrap font-mono text-lg font-bold">
            {current.target}
          </p>
          <p className="mt-3 text-sm leading-6 text-[#274f67]">{current.summary}</p>
        </div>
        <div className="hidden items-center justify-center md:flex" aria-hidden="true">
          <svg viewBox="0 0 48 24" className="w-10 fill-none stroke-[#075486] stroke-2">
            <path d="M2 12h40m0 0-8-8m8 8-8 8" />
          </svg>
        </div>
        <div
          className="min-w-0 rounded-[4px] border-2 border-[#075486] bg-[#b8d8e8] p-5"
          aria-live="polite"
        >
          <p className="font-mono text-xs font-bold tracking-[.12em] text-[#ef795e]">
            {copy.responseLabel}
          </p>
          <p className="mt-2 font-mono text-lg font-bold">{response}</p>
          <p className="mt-4 font-mono text-xs font-bold tracking-[.12em] text-[#ef795e]">
            {copy.stateLabel}
          </p>
          <p className="mt-2 text-lg font-bold">{state}</p>
          <p className="mt-3 font-mono text-sm">
            {copy.runsLabel}: {runs}
          </p>
          {runs > 1 && (
            <p className="mt-3 w-fit border-b-2 border-[#ef795e] font-bold">{current.verdict}</p>
          )}
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => setRuns((value) => value + 1)}
          className="rounded-[4px] bg-[#075486] px-5 py-3 text-sm font-bold text-[#fffaf0]"
        >
          {copy.runAction}
        </button>
        <button
          type="button"
          onClick={() => setRuns(0)}
          className="rounded-[4px] border-2 border-[#075486] bg-transparent px-5 py-[10px] text-sm font-bold"
        >
          {copy.resetAction}
        </button>
      </div>
    </section>
  )
}

import { useState } from 'react'
import { interactiveCopy } from '../../data/interactive-copy'

export default function CurlPlayground() {
  const copy = interactiveCopy.curl
  const [url, setUrl] = useState<string>(copy.presets[0].url)
  const [result, setResult] = useState<string>(copy.empty)
  const [loading, setLoading] = useState(false)
  const [activity, setActivity] = useState<string>(copy.activityIdle)
  const [activityState, setActivityState] = useState<'idle' | 'sending' | 'response' | 'failure'>(
    'idle'
  )

  async function run() {
    setLoading(true)
    setResult(copy.loading)

    try {
      const requestUrl = new URL(url)
      setActivity(`${copy.activitySending} ${requestUrl.pathname}${requestUrl.search}`)
      setActivityState('sending')
      const response = await fetch(url)
      const body = await response.text()
      const lines = [
        `> GET ${requestUrl.pathname}${requestUrl.search}`,
        `< HTTP ${response.status} ${response.statusText || ''}`.trimEnd(),
      ]
      if (response.redirected) lines.push(`< final-url: ${response.url}`)
      if (body.trim()) lines.push('', body.slice(0, 500))
      setResult(lines.join('\n'))
      setActivity(`RESPONSE · ${response.status} ${response.statusText || ''}`.trimEnd())
      setActivityState('response')
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error)
      setResult(`${copy.failurePrefix}: ${message}\n\n${copy.fallback}\ncurl -i ${url}`)
      setActivity(copy.activityFailure)
      setActivityState('failure')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="my-10 border-y-2 border-[#075486] bg-[#b8d8e8] px-5 py-7 text-[#075486] not-prose sm:px-7">
      <p className="font-mono text-xs font-bold tracking-[.16em] text-[#ef795e]">{copy.eyebrow}</p>
      <h3 className="mt-2 text-2xl font-bold tracking-[-.03em] sm:text-3xl">{copy.title}</h3>
      <p className="mt-3 max-w-3xl text-base leading-7 text-[#274f67]">{copy.description}</p>

      <div className="mt-6">
        <p className="font-mono text-xs font-bold tracking-[.12em]">{copy.activityLabel}</p>
        <div className="relative mt-2 h-24 overflow-hidden rounded-t-[28px] border-x-2 border-t-2 border-[#075486] bg-[#fffaf0]">
          <div
            className={`absolute left-1/2 top-3 flex h-10 -translate-x-1/2 items-center justify-center rounded-full bg-[#101010] px-4 font-mono text-xs font-bold text-[#fffaf0] transition-[width,background-color] duration-300 ${
              activityState === 'idle' ? 'w-24' : 'w-[calc(100%-2rem)] max-w-[420px]'
            } ${activityState === 'failure' ? 'bg-[#9d382d]' : ''}`}
            aria-live="polite"
          >
            <span className="truncate">{activity}</span>
          </div>
        </div>
      </div>

      <label
        className="mt-6 block font-mono text-xs font-bold tracking-[.12em]"
        htmlFor="request-url"
      >
        {copy.urlLabel}
      </label>
      <div className="mt-2 grid min-w-0 gap-2 sm:grid-cols-[minmax(0,1fr)_auto]">
        <input
          id="request-url"
          type="url"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
          className="min-w-0 rounded-[4px] border-2 border-[#075486] bg-[#fffaf0] px-3 py-3 font-mono text-sm text-[#075486] outline-none focus:ring-2 focus:ring-[#ef795e]"
        />
        <button
          type="button"
          onClick={run}
          disabled={loading}
          className="rounded-[4px] bg-[#075486] px-5 py-3 text-sm font-bold text-[#fffaf0] disabled:opacity-50"
        >
          {loading ? copy.loading : copy.runAction}
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {copy.presets.map((preset) => (
          <button
            key={preset.label}
            type="button"
            onClick={() => setUrl(preset.url)}
            className="rounded-[4px] border-2 border-[#075486] bg-[#fffaf0] px-3 py-1.5 font-mono text-xs font-bold hover:bg-[#f4c84f]"
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="mt-5 overflow-hidden rounded-[10px] border border-[#a9a9a9] bg-[#101010]">
        <div
          className="flex h-9 items-center gap-2 border-b border-[#b8b8b8] bg-[#e8e8e8] px-3"
          aria-hidden="true"
        >
          <span className="h-3 w-3 rounded-full bg-[#ff5f57]"></span>
          <span className="h-3 w-3 rounded-full bg-[#febc2e]"></span>
          <span className="h-3 w-3 rounded-full bg-[#28c840]"></span>
          <span className="ml-2 font-mono text-xs text-[#333]">browser fetch</span>
        </div>
        <pre
          className="min-h-[132px] max-w-full overflow-x-auto whitespace-pre p-5 font-mono text-sm leading-7 text-[#f1f1ed]"
          aria-live="polite"
        >
          {result}
        </pre>
      </div>
    </section>
  )
}

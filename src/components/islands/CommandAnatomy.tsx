import { useState } from 'react'
import { interactiveCopy } from '../../data/interactive-copy'

export default function CommandAnatomy() {
  const copy = interactiveCopy.pythonServerAnatomy
  const [activeTokenId, setActiveTokenId] = useState('http-server')
  const [copied, setCopied] = useState(false)

  const activeToken = copy.tokens.find((item) => item.id === activeTokenId) ?? copy.tokens[2]

  const fullCommand = copy.tokens.map((item) => item.label).join(' ')

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullCommand)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Ignore clipboard write failure
    }
  }

  return (
    <section className="my-8 rounded-[8px] border-2 border-[#075486] bg-[#fffaf0] p-5 not-prose shadow-[4px_4px_0_#075486] sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#075486]/20 pb-3">
        <div>
          <p className="font-mono text-xs font-bold tracking-[.15em] text-[#ef795e]">
            {copy.eyebrow}
          </p>
          <h4 className="mt-1 text-lg font-bold tracking-[-.02em] text-[#075486] sm:text-xl">
            {copy.title}
          </h4>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          aria-label={copy.copyPrompt}
          className="inline-flex items-center gap-1.5 rounded-[4px] border border-[#075486]/40 bg-white px-3 py-1.5 font-mono text-xs font-bold text-[#075486] transition-colors hover:bg-[#b8d8e8]/50 focus-visible:outline-2 focus-visible:outline-[#ef795e]"
        >
          {copied ? (
            <span className="text-[#28a745]">{copy.copiedAlert}</span>
          ) : (
            <span>{copy.copyPrompt}</span>
          )}
        </button>
      </div>

      <p className="mt-3 text-sm text-[#4f7892]">{copy.prompt}</p>

      {/* Interactive Command Ribbon */}
      <div className="mt-4 flex flex-wrap items-center gap-2 rounded-[6px] border border-[#075486]/30 bg-[#101010] p-3">
        <span className="font-mono text-xs font-bold text-[#8fd36b] select-none">$</span>
        {copy.tokens.map((token) => {
          const isActive = token.id === activeTokenId
          return (
            <button
              key={token.id}
              type="button"
              onClick={() => setActiveTokenId(token.id)}
              onMouseEnter={() => setActiveTokenId(token.id)}
              aria-pressed={isActive}
              className={`rounded-[4px] px-3 py-1.5 font-mono text-sm font-bold transition-all duration-150 focus-visible:outline-2 focus-visible:outline-[#ef795e] ${
                isActive
                  ? 'bg-[#f4c84f] text-[#075486] shadow-sm ring-2 ring-[#ef795e]'
                  : 'bg-[#252525] text-[#d8d8d8] hover:bg-[#353535] hover:text-white'
              }`}
            >
              {token.label}
            </button>
          )
        })}
      </div>

      {/* Dynamic Token Inspector Card */}
      <div className="mt-4 rounded-[6px] border border-[#075486]/20 bg-white p-4 sm:p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-base font-bold text-[#075486]">{activeToken.label}</span>
          <span className="rounded-[3px] bg-[#b8d8e8] px-2.5 py-0.5 font-mono text-xs font-bold text-[#075486]">
            {activeToken.role}
          </span>
        </div>
        <p className="mt-2.5 text-base font-bold leading-7 text-[#075486]">{activeToken.summary}</p>
        <p className="mt-1.5 text-sm leading-6 text-[#4f7892]">{activeToken.detail}</p>
      </div>
    </section>
  )
}

import React, { useState } from 'react'
import { Link } from 'react-router-dom'

const COMMANDS = [
  {
    name: 'login',
    icon: 'login',
    accent: 'primary',
    desc: 'Authenticate CLI with Kritiq Cloud and store session token in ~/.kritiq/config.json.',
    usage: 'kritiq login --email dev@company.io',
    flags: '--email, -e · --password, -p',
  },
  {
    name: 'init',
    icon: 'rocket_launch',
    accent: 'tertiary',
    desc: 'Initialize workspace with .kritiq.json config and .kritiqignore rules.',
    usage: 'kritiq init',
    flags: 'No options',
  },
  {
    name: 'diff',
    icon: 'difference',
    accent: 'secondary',
    desc: 'Review changed lines from a specific Git ref using AI Engine with Groq fallback.',
    usage: 'kritiq diff HEAD~3',
    flags: 'REF (positional, default: HEAD)',
  },
  {
    name: 'review',
    icon: 'rate_review',
    accent: 'primary',
    desc: 'AI-powered code review with severity ratings, suggestions, and walkthrough generation.',
    usage: 'kritiq review app/main.py',
    flags: 'PATH (positional, required)',
  },
  {
    name: 'translate',
    icon: 'translate',
    accent: 'secondary',
    desc: 'Convert code between languages while preserving semantic logic and patterns.',
    usage: 'kritiq translate app.py --to java',
    flags: 'PATH (positional) · --to (required)',
  },
  {
    name: 'explain',
    icon: 'description',
    accent: 'tertiary',
    desc: 'Get deep architectural insights and plain-English summaries of complex files.',
    usage: 'kritiq explain cli/auth.py',
    flags: 'PATH (positional, required)',
  },
  {
    name: 'chat',
    icon: 'forum',
    accent: 'primary',
    desc: 'Start an interactive multi-turn AI chat session scoped to your codebase.',
    usage: 'kritiq chat',
    flags: 'No options · Type "exit" to quit',
  },
]

export default function CliPublicDocs() {
  const [copiedText, setCopiedText] = useState(null)

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    setCopiedText(text)
    setTimeout(() => setCopiedText(null), 2000)
  }

  return (
    <div className="bg-surface text-on-surface font-sans min-h-screen selection:bg-primary/30 flex flex-col">
      {/* Top Header Nav */}
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-margin h-16 bg-surface/80 backdrop-blur-md border-b border-outline-variant">
        <div className="flex flex-col">
          <Link to="/" className="text-headline-md font-bold text-primary tracking-[0.1em] leading-none">
            KRITIQ
          </Link>
          <span className="text-[10px] text-on-surface-variant opacity-60 uppercase font-semibold mt-1">
            INTELLIGENCE REFINED
          </span>
        </div>

        <nav className="hidden md:flex gap-lg">
          <Link to="/#features" className="text-on-surface-variant hover:text-primary font-body-md transition-colors">
            Features
          </Link>
          <Link to="/cli" className="text-primary font-bold border-b-2 border-primary font-body-md transition-colors">
            CLI
          </Link>
          <a href="#pricing" className="text-on-surface-variant hover:text-primary font-body-md transition-colors">
            Pricing
          </a>
          <Link to="/cli-docs" className="text-on-surface-variant hover:text-primary font-body-md transition-colors">
            Docs
          </Link>
        </nav>

        <div className="flex items-center gap-md">
          <Link
            to="/login"
            className="text-on-surface-variant hover:text-primary transition-colors font-body-md text-xs font-semibold px-sm py-xs"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="bg-primary-container text-on-primary-container px-md py-xs rounded-lg font-bold text-xs hover:brightness-110 active:opacity-80 transition-all"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Content Layout with Left Sub-nav */}
      <div className="pt-16 flex-1 flex">
        {/* Left Sub-nav Sidebar */}
        <aside className="w-56 border-r border-outline-variant bg-surface-container-low hidden md:block p-md space-y-md sticky top-16 h-[calc(100vh-4rem)]">
          <div>
            <h3 className="font-bold text-body-md text-on-surface">CLI Reference</h3>
            <p className="text-[10px] font-mono text-on-surface-variant opacity-60">v2.4.12-stable</p>
          </div>

          <nav className="space-y-xs text-xs font-label-caps uppercase">
            <a href="#installation" className="block px-sm py-xs text-on-surface-variant hover:text-on-surface transition-colors">
              INSTALLATION
            </a>
            <a href="#authentication" className="block px-sm py-xs text-on-surface-variant hover:text-on-surface transition-colors">
              AUTHENTICATION
            </a>
            <a href="#commands" className="block px-sm py-xs text-primary font-bold bg-surface-container-high border-l-2 border-primary">
              COMMANDS (7)
            </a>
            <a href="#fallback" className="block px-sm py-xs text-on-surface-variant hover:text-on-surface transition-colors">
              AI FALLBACK
            </a>
            <a href="#configuration" className="block px-sm py-xs text-on-surface-variant hover:text-on-surface transition-colors">
              CONFIGURATION
            </a>
            <a href="#demo" className="block px-sm py-xs text-on-surface-variant hover:text-on-surface transition-colors">
              LIVE DEMO
            </a>
          </nav>

          {/* Quick Jump Links */}
          <div className="pt-md border-t border-outline-variant space-y-xs">
            <p className="text-[10px] font-label-caps uppercase text-on-surface-variant tracking-wider font-bold">Commands</p>
            {COMMANDS.map((cmd) => (
              <a
                key={cmd.name}
                href={`#cmd-${cmd.name}`}
                className="block px-sm py-0.5 text-[11px] font-mono text-on-surface-variant hover:text-primary transition-colors"
              >
                {cmd.name}
              </a>
            ))}
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 p-lg max-w-5xl mx-auto space-y-xl">
          {/* Header Title */}
          <div className="space-y-xs">
            <span className="px-xs py-0.5 rounded text-[10px] font-label-caps uppercase bg-primary-container/20 text-primary border border-primary/30">
              STABLE V2.4.12
            </span>
            <h1 className="font-display text-display lg:text-[40px] text-on-surface">KRITIQ CLI</h1>
            <p className="font-body-lg text-on-surface-variant max-w-2xl text-sm leading-relaxed">
              7 powerful commands for AI-driven code review, translation, explanation, and interactive chat — directly from your terminal. Powered by <span className="text-primary font-semibold">Gemini 2.5 Flash</span> with automatic <span className="text-secondary font-semibold">Groq Llama-3</span> fallback.
            </p>
          </div>

          {/* 1. Installation */}
          <section id="installation" className="space-y-sm pt-md border-t border-outline-variant">
            <div className="flex items-center gap-xs">
              <span className="w-6 h-6 rounded-full bg-primary-container/30 text-primary font-bold text-xs flex items-center justify-center">
                1
              </span>
              <h2 className="font-headline-md text-headline-md text-on-surface">Installation</h2>
            </div>
            <p className="text-on-surface-variant text-xs">
              Get started by cloning the repository and installing dependencies. Requires Python 3.8+ and pip.
            </p>

            <div className="space-y-sm">
              <div className="relative bg-surface-container border border-outline-variant rounded-lg p-md font-mono text-code-sm flex justify-between items-center">
                <code className="text-tertiary text-xs">$ pip install -r requirements.txt</code>
                <button
                  onClick={() => handleCopy('pip install -r requirements.txt')}
                  className="text-[10px] text-on-surface-variant hover:text-primary transition-colors flex items-center gap-0.5 font-sans"
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {copiedText === 'pip install -r requirements.txt' ? 'check' : 'content_copy'}
                  </span>
                  {copiedText === 'pip install -r requirements.txt' ? 'Copied' : 'COPY'}
                </button>
              </div>

              <div className="relative bg-surface-container border border-outline-variant rounded-lg p-md font-mono text-code-sm flex justify-between items-center">
                <code className="text-tertiary text-xs">$ python -m cli.main --help</code>
                <button
                  onClick={() => handleCopy('python -m cli.main --help')}
                  className="text-[10px] text-on-surface-variant hover:text-primary transition-colors flex items-center gap-0.5 font-sans"
                >
                  <span className="material-symbols-outlined text-[14px]">
                    {copiedText === 'python -m cli.main --help' ? 'check' : 'content_copy'}
                  </span>
                  {copiedText === 'python -m cli.main --help' ? 'Copied' : 'COPY'}
                </button>
              </div>
            </div>
          </section>

          {/* 2. Authentication */}
          <section id="authentication" className="space-y-sm pt-md border-t border-outline-variant">
            <div className="flex items-center gap-xs">
              <span className="w-6 h-6 rounded-full bg-primary-container/30 text-primary font-bold text-xs flex items-center justify-center">
                2
              </span>
              <h2 className="font-headline-md text-headline-md text-on-surface">Authentication</h2>
            </div>
            <p className="text-on-surface-variant text-xs">
              Connect your CLI to your KRITIQ account. This stores a session JWT token in <code className="text-primary">~/.kritiq/config.json</code>.
            </p>

            <div className="bg-surface-container border border-outline-variant rounded-lg p-md font-mono text-code-sm space-y-1 text-xs">
              <div className="text-tertiary">$ kritiq login --email dev@company.io</div>
              <div className="text-on-surface-variant">Enter Password (min 8 chars): ••••••••</div>
              <div className="text-on-surface-variant">Logging into Kritiq Cloud...</div>
              <div className="text-[#4edea3]">✔ Success. Session token stored in ~/.kritiq/config.json</div>
            </div>

            <div className="p-sm bg-surface-container-high border border-outline-variant rounded-lg flex items-center gap-xs text-[11px] text-on-surface-variant">
              <span className="material-symbols-outlined text-primary text-[16px]">info</span>
              Your credentials are stored securely in your home directory. Use <code className="text-primary">--email</code> and <code className="text-primary">--password</code> flags for non-interactive mode, or omit them for interactive prompts.
            </div>
          </section>

          {/* 3. All Commands Grid */}
          <section id="commands" className="space-y-md pt-md border-t border-outline-variant">
            <div className="flex items-center justify-between">
              <h2 className="font-headline-md text-headline-md text-on-surface">Core Commands</h2>
              <span className="text-[10px] font-mono text-on-surface-variant uppercase">7 commands registered</span>
            </div>

            <div className="grid md:grid-cols-2 gap-md">
              {COMMANDS.map((cmd) => (
                <div key={cmd.name} id={`cmd-${cmd.name}`} className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm hover:border-primary/30 transition-all">
                  <div className={`flex items-center gap-xs text-${cmd.accent} font-bold text-body-md`}>
                    <span className="material-symbols-outlined text-[20px]">{cmd.icon}</span>
                    {cmd.name}
                  </div>
                  <p className="text-on-surface-variant text-xs leading-relaxed">
                    {cmd.desc}
                  </p>
                  <div className="bg-surface-container-lowest p-xs rounded font-mono text-[11px] text-tertiary flex items-center justify-between">
                    <span>$ {cmd.usage}</span>
                    <button
                      onClick={() => handleCopy(cmd.usage)}
                      className="text-[10px] text-on-surface-variant hover:text-primary transition-colors ml-2 flex-shrink-0"
                    >
                      <span className="material-symbols-outlined text-[14px]">
                        {copiedText === cmd.usage ? 'check' : 'content_copy'}
                      </span>
                    </button>
                  </div>
                  <div className="text-[10px] text-on-surface-variant font-mono">
                    <span className="text-on-surface-variant/60">flags:</span> {cmd.flags}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 4. AI Fallback Architecture */}
          <section id="fallback" className="space-y-md pt-md border-t border-outline-variant">
            <h2 className="font-headline-md text-headline-md text-on-surface">Zero-Downtime AI Fallback</h2>
            <p className="text-on-surface-variant text-xs max-w-2xl">
              All AI-powered commands (<code className="text-primary">review</code>, <code className="text-primary">translate</code>, <code className="text-primary">diff</code>, <code className="text-primary">explain</code>) use a dual-engine architecture for guaranteed uptime:
            </p>

            <div className="grid md:grid-cols-3 gap-md">
              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-xs">
                <div className="flex items-center gap-xs text-primary font-bold text-body-md">
                  <span className="material-symbols-outlined text-[20px]">neurology</span>
                  Primary Engine
                </div>
                <p className="text-on-surface-variant text-xs">
                  <span className="text-primary font-semibold">Gemini 2.5 Flash</span> — Google's fastest model for code analysis, reviews, and translations.
                </p>
              </div>

              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-xs">
                <div className="flex items-center gap-xs text-secondary font-bold text-body-md">
                  <span className="material-symbols-outlined text-[20px]">swap_horiz</span>
                  Fallback Trigger
                </div>
                <p className="text-on-surface-variant text-xs">
                  On <span className="text-error font-semibold">504 DEADLINE_EXCEEDED</span> or any Gemini exception, the request is instantly rerouted.
                </p>
              </div>

              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-xs">
                <div className="flex items-center gap-xs text-tertiary font-bold text-body-md">
                  <span className="material-symbols-outlined text-[20px]">bolt</span>
                  Fallback Engine
                </div>
                <p className="text-on-surface-variant text-xs">
                  <span className="text-tertiary font-semibold">Groq Llama-3</span> — Sub-second inference for uninterrupted code processing.
                </p>
              </div>
            </div>

            <div className="bg-surface-container border border-outline-variant rounded-lg p-md font-mono text-code-sm space-y-1 text-[11px]">
              <div className="text-on-surface-variant"># Example fallback in action:</div>
              <div className="text-tertiary">$ kritiq review large_module.py</div>
              <div className="text-on-surface-variant">Reviewing large_module.py (detected language: python)...</div>
              <div className="text-[#fbbf24]">[Gemini timeout: 504 DEADLINE_EXCEEDED] Switching to Groq Llama-3 fallback...</div>
              <div className="text-on-surface-variant">── 2 Critical vulnerabilities found</div>
              <div className="text-on-surface-variant">── 5 Style suggestions</div>
              <div className="text-[#4edea3]">✔ Review complete.</div>
            </div>
          </section>

          {/* 5. Configuration */}
          <section id="configuration" className="space-y-sm pt-md border-t border-outline-variant">
            <h2 className="font-headline-md text-headline-md text-on-surface">Configuration</h2>

            <div className="grid md:grid-cols-2 gap-md">
              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                <h3 className="font-bold text-body-md text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-primary text-[18px]">data_object</span>
                  .kritiq.json
                </h3>
                <div className="bg-surface-container-lowest p-xs rounded font-mono text-[11px] text-on-surface-variant border border-outline-variant/40">
                  <div>{'{'}</div>
                  <div className="pl-3"><span className="text-secondary">"version"</span>: <span className="text-tertiary">"2.4.12-stable"</span>,</div>
                  <div className="pl-3"><span className="text-secondary">"engine"</span>: <span className="text-tertiary">"gemini-2.5-flash"</span>,</div>
                  <div className="pl-3"><span className="text-secondary">"max_file_size_kb"</span>: <span className="text-primary">500</span>,</div>
                  <div className="pl-3"><span className="text-secondary">"rules"</span>: [<span className="text-tertiary">"security"</span>,</div>
                  <div className="pl-6"><span className="text-tertiary">"performance"</span>,</div>
                  <div className="pl-6"><span className="text-tertiary">"code_smells"</span>]</div>
                  <div>{'}'}</div>
                </div>
              </div>

              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                <h3 className="font-bold text-body-md text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-secondary text-[18px]">visibility_off</span>
                  .kritiqignore
                </h3>
                <div className="bg-surface-container-lowest p-xs rounded font-mono text-[11px] text-on-surface-variant border border-outline-variant/40">
                  <div className="text-on-surface-variant/60"># Kritiq Ignore Rules</div>
                  <div>node_modules/</div>
                  <div>dist/</div>
                  <div>build/</div>
                  <div>.git/</div>
                  <div>venv/</div>
                  <div>__pycache__/</div>
                  <div>*.min.js</div>
                  <div>*.pyc</div>
                </div>
              </div>
            </div>
          </section>

          {/* 6. Live Session Demo */}
          <section id="demo" className="space-y-sm pt-md border-t border-outline-variant">
            <div className="flex justify-between items-center">
              <h2 className="font-headline-md text-headline-md text-on-surface">Live Session Demo</h2>
              <span className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase">
                Cross-platform: macOS, Linux, Windows
              </span>
            </div>

            <div className="bg-surface-container rounded-xl border border-outline-variant overflow-hidden code-glow font-mono text-code-sm">
              <div className="flex items-center justify-between px-md py-xs bg-surface-container-high border-b border-outline-variant">
                <div className="flex items-center gap-xs">
                  <div className="w-3 h-3 rounded-full bg-error/60"></div>
                  <div className="w-3 h-3 rounded-full bg-secondary/60"></div>
                  <div className="w-3 h-3 rounded-full bg-tertiary/60"></div>
                </div>
                <div className="text-[11px] text-on-surface-variant opacity-60">kritiq — bash — 80×24</div>
                <div className="w-10"></div>
              </div>

              <div className="p-md space-y-xs leading-relaxed text-[12px]">
                {/* login */}
                <div className="text-[#58a6ff] font-bold">$ kritiq login --email dev@company.io</div>
                <div className="text-on-surface-variant text-[11px]">Logging into Kritiq Cloud...</div>
                <div className="text-[#4edea3] text-[11px]">✔ Success. Session token stored in ~/.kritiq/config.json</div>

                {/* init */}
                <div className="text-[#58a6ff] font-bold mt-2">$ kritiq init</div>
                <div className="text-[#4edea3] text-[11px]">✔ Created .kritiq.json project configuration.</div>
                <div className="text-[#4edea3] text-[11px]">✔ Created .kritiqignore file.</div>
                <div className="text-[#4edea3] text-[11px] font-bold">✔ Kritiq workspace initialized successfully!</div>

                {/* review */}
                <div className="text-[#58a6ff] font-bold mt-2">$ kritiq review app/utils/validators.py</div>
                <div className="text-on-surface-variant text-[11px]">Reviewing app/utils/validators.py (detected language: python)...</div>
                <div className="flex gap-md py-xs">
                  <span className="bg-error-container/40 text-on-error-container border border-error/30 px-xs py-0.5 rounded font-label-caps text-[10px]">
                    2 Critical
                  </span>
                  <span className="bg-secondary-container/40 text-on-secondary-container border border-secondary/30 px-xs py-0.5 rounded font-label-caps text-[10px]">
                    5 Suggestions
                  </span>
                </div>
                <div className="text-[#4edea3] text-[11px]">✔ Review walkthrough saved.</div>

                {/* translate */}
                <div className="text-[#58a6ff] font-bold mt-2">$ kritiq translate app.py --to java</div>
                <div className="text-on-surface-variant text-[11px]">Translating app.py (from python to java)...</div>
                <div className="text-on-surface-variant text-[11px]">// Translated output: public class App {'{ ... }'}</div>

                {/* chat */}
                <div className="text-[#58a6ff] font-bold mt-2">$ kritiq chat</div>
                <div className="text-[#22d3ee] text-[11px]">Welcome to the KRITIQ Chat Interface!</div>
                <div className="text-[#c084fc] text-[11px]">You: How can I optimize my database queries?</div>
                <div className="text-on-surface-variant text-[11px]">Kritiq is thinking...</div>
                <div className="text-[#a78bfa] text-[11px] font-bold">Kritiq: Consider using indexed columns, batch operations...</div>

                {/* cursor */}
                <div className="flex items-center gap-xs pt-xs">
                  <span className="text-[#4edea3]">$</span>
                  <span className="w-2 h-4 bg-on-surface inline-block animate-pulse"></span>
                </div>
              </div>
            </div>
          </section>

          {/* Bottom CTA Banner */}
          <section className="p-xl bg-surface-container border border-outline-variant rounded-xl flex flex-col md:flex-row justify-between items-center gap-md">
            <div>
              <h3 className="font-display text-headline-lg text-on-surface">Ready to elevate your code?</h3>
              <p className="text-xs text-on-surface-variant mt-xs">Prefer a visual interface? Try the KRITIQ web app →</p>
            </div>
            <Link
              to="/dashboard"
              className="bg-primary-container text-on-primary-container px-xl py-md rounded-lg font-bold text-xs hover:brightness-110 active:scale-[0.98] transition-all flex items-center gap-xs whitespace-nowrap"
            >
              Go to Web App
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </Link>
          </section>
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-outline-variant py-lg px-margin text-center text-on-surface-variant text-body-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-md text-xs">
          <p>© 2026 KRITIQ AI. Built for high-performance engineering.</p>
          <div className="flex gap-md">
            <a href="#privacy" className="hover:text-primary transition-colors">Privacy</a>
            <a href="#terms" className="hover:text-primary transition-colors">Terms</a>
            <a href="https://github.com/octocat/Hello-World" target="_blank" rel="noreferrer" className="hover:text-primary transition-colors">GitHub</a>
            <a href="#changelog" className="hover:text-primary transition-colors">Changelog</a>
          </div>
        </div>
      </footer>
    </div>
  )
}

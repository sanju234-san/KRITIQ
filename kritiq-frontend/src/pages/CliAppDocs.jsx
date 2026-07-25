import React, { useState } from 'react'
import Sidebar from '../components/Sidebar'
import NavBar from '../components/NavBar'

const CLI_COMMANDS = [
  {
    name: 'login',
    icon: 'login',
    color: 'primary',
    tagline: 'Authenticate with Kritiq Cloud',
    description: 'Authenticate CLI with Kritiq Cloud service and store session token in ~/.kritiq/config.json.',
    usage: 'kritiq login [OPTIONS]',
    options: [
      { flag: '--email, -e', type: 'TEXT', desc: 'Work email address' },
      { flag: '--password, -p', type: 'TEXT', desc: 'Account password (min 8 chars, hidden input)' },
    ],
    example: {
      command: 'kritiq login --email dev@company.io',
      output: [
        { text: 'Enter Password (min 8 chars): ••••••••', style: 'muted' },
        { text: 'Logging into Kritiq Cloud...', style: 'muted' },
        { text: '✔ Success. Session token stored in ~/.kritiq/config.json', style: 'success' },
      ],
    },
    notes: 'If --email or --password are omitted, interactive prompts will appear. Credentials are stored locally in ~/.kritiq/config.json.',
    sourceFile: 'cli/commands/login.py',
    sourceSnippet: `def login(
    email: str = typer.Option(None, "--email", "-e"),
    password: str = typer.Option(None, "--password", "-p")
):
    resp = requests.post(
        "http://localhost:8000/auth/login",
        json={"email": email, "password": password}
    )
    token = resp.json().get("access_token", "")
    store_token(token, email)`,
  },
  {
    name: 'init',
    icon: 'rocket_launch',
    color: 'tertiary',
    tagline: 'Initialize Kritiq workspace',
    description: 'Initialize Kritiq configuration (.kritiq.json) and ignore rules (.kritiqignore) in the current directory.',
    usage: 'kritiq init',
    options: [],
    example: {
      command: 'kritiq init',
      output: [
        { text: '✔ Created .kritiq.json project configuration.', style: 'success' },
        { text: '✔ Created .kritiqignore file.', style: 'success' },
        { text: '✔ Kritiq workspace initialized successfully!', style: 'success-bold' },
      ],
    },
    notes: 'Creates .kritiq.json with default engine config (gemini-2.5-flash, rules: security/performance/code_smells) and .kritiqignore excluding node_modules, dist, __pycache__, etc.',
    sourceFile: 'cli/commands/init.py',
    sourceSnippet: `config_data = {
    "version": "2.4.12-stable",
    "engine": "gemini-2.5-flash",
    "max_file_size_kb": 500,
    "rules": ["security", "performance", "code_smells"]
}
# Creates .kritiq.json and .kritiqignore`,
  },
  {
    name: 'diff',
    icon: 'difference',
    color: 'secondary',
    tagline: 'Review git diff patches',
    description: 'Review only changed lines from a specific Git reference or modified workspace files. Uses AI Engine with automatic Groq Llama-3 fallback.',
    usage: 'kritiq diff [REF]',
    options: [
      { flag: 'REF', type: 'TEXT', desc: 'Git reference or commit to diff against (default: HEAD)' },
    ],
    example: {
      command: 'kritiq diff HEAD~3',
      output: [
        { text: 'Scanning git diff against \'HEAD~3\'...', style: 'muted' },
        { text: 'Analyzing diff patch with AI Engine...', style: 'muted' },
        { text: '── Critical: SQL injection vulnerability in line 42', style: 'error' },
        { text: '── Suggestion: Use parameterized queries instead', style: 'warning' },
        { text: '✔ Diff review complete.', style: 'success' },
      ],
    },
    notes: 'Runs `git diff <ref>` internally with UTF-8 encoding. If Gemini times out (504), automatically falls back to Groq Llama-3.',
    sourceFile: 'cli/commands/diff.py',
    sourceSnippet: `result = subprocess.run(
    ["git", "diff", ref],
    capture_output=True, text=True,
    encoding="utf-8", errors="replace"
)
review_result = review_code(diff_text, language="gitpatch")
# Falls back to ask_groq() on Gemini timeout`,
  },
  {
    name: 'review',
    icon: 'rate_review',
    color: 'primary',
    tagline: 'AI-powered code review',
    description: 'Review a code file using the Gemini AI agent with automatic Groq Llama-3 fallback. Generates a review walkthrough summary.',
    usage: 'kritiq review <PATH>',
    options: [
      { flag: 'PATH', type: 'TEXT', desc: 'Path to the file to review (required)' },
    ],
    example: {
      command: 'kritiq review app/utils/validators.py',
      output: [
        { text: 'Reviewing app/utils/validators.py (detected language: python)...', style: 'muted' },
        { text: '', style: 'muted' },
        { text: '── CRITICAL: Unhandled edge case in validator at line 42', style: 'error' },
        { text: '── MEDIUM: Redundant null check at line 15', style: 'warning' },
        { text: '── LOW: Consider using enumerate() for readability', style: 'info' },
        { text: '', style: 'muted' },
        { text: 'Review walkthrough saved to: walkthroughs/review_validators.md', style: 'success' },
      ],
    },
    notes: 'Auto-detects language from file extension. Generates walkthrough files via walkthrough_writer. Falls back to Groq Llama-3 on Gemini timeout.',
    sourceFile: 'cli/commands/review.py',
    sourceSnippet: `language = detect_language(path)
review_result = review_code(code_content, language, file_path=path)
# On Gemini failure:
prompt = build_review_prompt(code_content, language=language)
review_result = ask_groq(prompt)
# Auto-saves walkthrough summary`,
  },
  {
    name: 'translate',
    icon: 'translate',
    color: 'secondary',
    tagline: 'Cross-language code translation',
    description: 'Translate a code file to another language using Gemini AI with automatic Groq Llama-3 fallback.',
    usage: 'kritiq translate <PATH> --to <LANGUAGE>',
    options: [
      { flag: 'PATH', type: 'TEXT', desc: 'Path to the file to translate (required)' },
      { flag: '--to', type: 'TEXT', desc: 'Target language for translation (required)' },
    ],
    example: {
      command: 'kritiq translate app.py --to java',
      output: [
        { text: 'Translating app.py (from python to java)...', style: 'muted' },
        { text: '', style: 'muted' },
        { text: '// Translated Java output:', style: 'info' },
        { text: 'public class App {', style: 'code' },
        { text: '    public static void main(String[] args) { ... }', style: 'code' },
        { text: '}', style: 'code' },
        { text: '', style: 'muted' },
        { text: 'Translation walkthrough saved to: walkthroughs/translate_app.md', style: 'success' },
      ],
    },
    notes: 'Auto-detects source language from file extension. Supports Python, JavaScript, TypeScript, Go, Java, Rust, C/C++. Falls back to Groq Llama-3 on Gemini timeout.',
    sourceFile: 'cli/commands/translate.py',
    sourceSnippet: `source_language = detect_language(path)
translation_result = translate_code(
    code_content, source_language, to, file_path=path
)
# On Gemini failure:
prompt = build_translation_prompt(code_content, source_language, to)
translation_result = ask_groq(prompt)`,
  },
  {
    name: 'explain',
    icon: 'description',
    color: 'tertiary',
    tagline: 'Plain-language code explanation',
    description: 'Explain what a code file does in plain language using the Gemini AI agent. Generates an explanation walkthrough.',
    usage: 'kritiq explain <PATH>',
    options: [
      { flag: 'PATH', type: 'TEXT', desc: 'Path to the file to explain (required)' },
    ],
    example: {
      command: 'kritiq explain cli/auth.py',
      output: [
        { text: 'Explaining cli/auth.py (detected language: python)...', style: 'muted' },
        { text: '', style: 'muted' },
        { text: 'This module handles CLI authentication token management.', style: 'info' },
        { text: 'It reads/writes JWT tokens to ~/.kritiq/config.json...', style: 'info' },
        { text: '', style: 'muted' },
        { text: 'Explanation walkthrough saved to: walkthroughs/explain_auth.md', style: 'success' },
      ],
    },
    notes: 'Uses explanation_service for deep architectural insight. Auto-generates walkthrough documentation.',
    sourceFile: 'cli/commands/explain.py',
    sourceSnippet: `language = detect_language(path)
explanation_result = explain_code(
    code_content, language, file_path=path
)
saved_path = write_explanation_walkthrough(
    path, language, explanation_result
)`,
  },
  {
    name: 'chat',
    icon: 'forum',
    color: 'primary',
    tagline: 'Interactive AI chat session',
    description: 'Start an interactive chat session with Kritiq. Ask questions about your code, reviews, or files. Type "exit" or "quit" to end.',
    usage: 'kritiq chat',
    options: [],
    example: {
      command: 'kritiq chat',
      output: [
        { text: '===================================================', style: 'accent' },
        { text: '     Welcome to the KRITIQ Chat Interface!', style: 'accent-bold' },
        { text: ' Ask questions about your code, reviews, or files.', style: 'accent' },
        { text: ' Type \'exit\' or \'quit\' to end the session.', style: 'warning' },
        { text: '===================================================', style: 'accent' },
        { text: '', style: 'muted' },
        { text: 'You: How can I optimize my database queries?', style: 'user' },
        { text: 'Kritiq is thinking...', style: 'muted' },
        { text: 'Kritiq: Consider using indexed columns, batch operations...', style: 'ai' },
      ],
    },
    notes: 'Uses chat_service.chat_turn() for multi-turn conversations with full history context. Ctrl+C gracefully exits.',
    sourceFile: 'cli/commands/chat.py',
    sourceSnippet: `conversation_history = []
while True:
    user_input = typer.prompt("You")
    if user_input.strip().lower() in ("exit", "quit"):
        break
    response, conversation_history = chat_turn(
        user_input, conversation_history
    )`,
  },
]

function getOutputStyle(style) {
  switch (style) {
    case 'success': return 'text-[#4edea3]'
    case 'success-bold': return 'text-[#4edea3] font-bold'
    case 'error': return 'text-[#f87171]'
    case 'warning': return 'text-[#fbbf24]'
    case 'info': return 'text-[#60a5fa]'
    case 'accent': return 'text-[#22d3ee]'
    case 'accent-bold': return 'text-[#22d3ee] font-bold'
    case 'user': return 'text-[#c084fc]'
    case 'ai': return 'text-[#a78bfa] font-bold'
    case 'code': return 'text-[#94a3b8] pl-4'
    default: return 'text-on-surface-variant'
  }
}

export default function CliAppDocs() {
  const [activeCommand, setActiveCommand] = useState(null)
  const [showSource, setShowSource] = useState({})
  const [copiedCmd, setCopiedCmd] = useState(null)

  const toggleSource = (name) => {
    setShowSource((prev) => ({ ...prev, [name]: !prev[name] }))
  }

  const copyToClipboard = (text, name) => {
    navigator.clipboard.writeText(text)
    setCopiedCmd(name)
    setTimeout(() => setCopiedCmd(null), 2000)
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />

      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <NavBar title="CLI Documentation" />

        <main className="mt-16 p-lg space-y-xl max-w-7xl mx-auto w-full">
          {/* Header */}
          <div className="space-y-xs">
            <div className="inline-flex items-center gap-xs text-[10px] font-label-caps uppercase text-primary tracking-widest font-bold">
              <span className="material-symbols-outlined text-[14px]">terminal</span>
              INTERFACE REFERENCE
            </div>
            <h1 className="font-display text-display text-on-surface">Command Line Interface</h1>
            <p className="font-body-lg text-on-surface-variant max-w-3xl text-sm leading-relaxed">
              The <span className="text-primary font-bold">Kritiq CLI</span> provides 7 commands for AI-powered code review, translation, explanation, and interactive chat — all from your terminal. Powered by <span className="text-tertiary font-semibold">Gemini 2.5 Flash</span> with automatic <span className="text-secondary font-semibold">Groq Llama-3</span> fallback.
            </p>
          </div>

          {/* Architecture Overview */}
          <div className="grid lg:grid-cols-3 gap-lg items-start">
            {/* Left 2 Cols: Live Terminal + Entrypoint */}
            <div className="lg:col-span-2 space-y-md">
              {/* Interactive Terminal Mockup */}
              <div className="bg-surface-container rounded-xl border border-outline-variant overflow-hidden code-glow font-mono text-code-sm shadow-2xl">
                <div className="flex items-center justify-between px-md py-xs bg-surface-container-high border-b border-outline-variant">
                  <div className="flex items-center gap-xs">
                    <div className="w-3 h-3 rounded-full bg-error/60"></div>
                    <div className="w-3 h-3 rounded-full bg-secondary/60"></div>
                    <div className="w-3 h-3 rounded-full bg-tertiary/60"></div>
                  </div>
                  <div className="flex items-center gap-xs text-[11px] text-on-surface-variant opacity-60">
                    <span className="material-symbols-outlined text-[14px]">lock</span>
                    bash — kritiq-cli v2.4.12
                  </div>
                  <div className="w-10"></div>
                </div>

                <div className="p-md space-y-md leading-relaxed text-[12px]">
                  {/* login */}
                  <div className="space-y-xs">
                    <div className="flex items-center gap-xs text-tertiary font-bold">
                      <span>➔</span>
                      <span className="text-on-surface">~</span>
                      <span className="text-on-surface font-bold">kritiq login --email dev@company.io</span>
                    </div>
                    <div className="pl-md text-on-surface-variant text-[11px]">Logging into Kritiq Cloud...</div>
                    <div className="pl-md text-[#4edea3] text-[11px] flex items-center gap-xs">
                      <span>✔</span> Success. Session token stored in ~/.kritiq/config.json
                    </div>
                  </div>

                  {/* init */}
                  <div className="space-y-xs pt-xs">
                    <div className="flex items-center gap-xs text-tertiary font-bold">
                      <span>➔</span>
                      <span className="text-on-surface">my-project</span>
                      <span className="text-on-surface font-bold">kritiq init</span>
                    </div>
                    <div className="pl-md text-[#4edea3] text-[11px]">✔ Created .kritiq.json project configuration.</div>
                    <div className="pl-md text-[#4edea3] text-[11px]">✔ Created .kritiqignore file.</div>
                    <div className="pl-md text-[#4edea3] text-[11px] font-bold">✔ Kritiq workspace initialized successfully!</div>
                  </div>

                  {/* review with fallback */}
                  <div className="space-y-xs pt-xs">
                    <div className="flex items-center gap-xs text-tertiary font-bold">
                      <span>➔</span>
                      <span className="text-on-surface">my-project</span>
                      <span className="text-on-surface-variant text-[10px]">git:(<span className="text-error">main</span>)</span>
                      <span className="text-on-surface font-bold">kritiq review app/main.py</span>
                    </div>
                    <div className="pl-md space-y-xs text-[11px]">
                      <p className="text-on-surface-variant">Reviewing app/main.py (detected language: python)...</p>
                      <p className="text-[#fbbf24] flex items-center gap-xs">
                        [Gemini timeout] Switching to Groq Llama-3 fallback...
                      </p>
                      <div className="flex gap-md py-xs">
                        <span className="bg-error-container/40 text-on-error-container border border-error/30 px-xs py-0.5 rounded font-label-caps text-[10px]">
                          1 Critical
                        </span>
                        <span className="bg-secondary-container/40 text-on-secondary-container border border-secondary/30 px-xs py-0.5 rounded font-label-caps text-[10px]">
                          3 Suggestions
                        </span>
                      </div>
                      <p className="text-[#4edea3] flex items-center gap-xs">
                        <span>✔</span> Review walkthrough saved.
                      </p>
                    </div>
                  </div>

                  {/* cursor */}
                  <div className="flex items-center gap-xs text-tertiary font-bold pt-xs">
                    <span>➔</span>
                    <span className="text-on-surface">my-project</span>
                    <span className="text-on-surface font-bold">kritiq chat</span>
                    <span className="w-2 h-4 bg-on-surface inline-block animate-pulse ml-1"></span>
                  </div>
                </div>
              </div>

              {/* Entrypoint & Config */}
              <div className="grid sm:grid-cols-2 gap-md">
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                  <div className="flex items-center gap-xs text-primary font-bold text-body-md">
                    <span className="material-symbols-outlined text-[18px]">data_object</span>
                    Entrypoint
                  </div>
                  <div className="font-mono text-[11px] text-on-surface-variant bg-surface-container-lowest p-xs rounded border border-outline-variant/40">
                    <div className="text-on-surface-variant">cli/main.py</div>
                    <div className="text-primary mt-1">app = typer.Typer()</div>
                    <div className="text-tertiary">app.command("login")(login)</div>
                    <div className="text-tertiary">app.command("init")(init)</div>
                    <div className="text-tertiary">app.command("diff")(diff)</div>
                    <div className="text-tertiary">app.command("review")(review)</div>
                    <div className="text-tertiary">app.command("translate")(translate)</div>
                    <div className="text-tertiary">app.command("explain")(explain)</div>
                    <div className="text-tertiary">app.command("chat")(chat)</div>
                  </div>
                </div>

                <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                  <div className="flex items-center gap-xs text-tertiary font-bold text-body-md">
                    <span className="material-symbols-outlined text-[18px]">settings</span>
                    .kritiq.json Config
                  </div>
                  <div className="font-mono text-[11px] text-on-surface-variant bg-surface-container-lowest p-xs rounded border border-outline-variant/40">
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
              </div>
            </div>

            {/* Right Column: Quick Reference */}
            <div className="space-y-md">
              {/* Command Overview */}
              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-md">
                <h3 className="font-bold text-body-md text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-primary text-[18px]">menu_book</span>
                  All Commands ({CLI_COMMANDS.length})
                </h3>

                <div className="space-y-sm">
                  {CLI_COMMANDS.map((cmd) => (
                    <button
                      key={cmd.name}
                      onClick={() => setActiveCommand(activeCommand === cmd.name ? null : cmd.name)}
                      className={`w-full text-left p-xs rounded-lg border transition-all ${
                        activeCommand === cmd.name
                          ? 'bg-primary/10 border-primary/40'
                          : 'bg-surface-container-lowest border-outline-variant/40 hover:border-primary/30 hover:bg-surface-container-high'
                      }`}
                    >
                      <div className="flex items-center gap-xs">
                        <span className={`material-symbols-outlined text-[16px] text-${cmd.color}`}>{cmd.icon}</span>
                        <code className="text-tertiary font-mono text-[11px] font-bold">{cmd.name}</code>
                      </div>
                      <p className="text-[10px] text-on-surface-variant mt-0.5 pl-5">{cmd.tagline}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* AI Fallback Flow */}
              <div className="p-md bg-primary-container/10 border border-primary/30 rounded-xl space-y-sm">
                <h4 className="font-bold text-body-sm text-primary flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">swap_horiz</span>
                  AI Fallback Flow
                </h4>
                <div className="space-y-xs text-[11px]">
                  <div className="flex items-center gap-xs">
                    <div className="w-5 h-5 rounded bg-primary/20 flex items-center justify-center text-primary text-[10px] font-bold">1</div>
                    <span className="text-on-surface">Gemini 2.5 Flash <span className="text-on-surface-variant">(primary)</span></span>
                  </div>
                  <div className="flex items-center gap-xs pl-2">
                    <span className="material-symbols-outlined text-[12px] text-on-surface-variant">arrow_downward</span>
                    <span className="text-[10px] text-on-surface-variant italic">on 504 timeout</span>
                  </div>
                  <div className="flex items-center gap-xs">
                    <div className="w-5 h-5 rounded bg-secondary/20 flex items-center justify-center text-secondary text-[10px] font-bold">2</div>
                    <span className="text-on-surface">Groq Llama-3 <span className="text-on-surface-variant">(fallback)</span></span>
                  </div>
                </div>
              </div>

              {/* Token Storage */}
              <div className="p-md bg-surface-container border border-dashed border-outline-variant rounded-xl space-y-sm">
                <h4 className="font-bold text-body-sm text-on-surface flex items-center gap-xs">
                  <span className="material-symbols-outlined text-secondary text-[16px]">key</span>
                  Token Storage
                </h4>
                <div className="text-[11px] text-on-surface-variant space-y-xs">
                  <div className="font-mono bg-surface-container-lowest p-xs rounded border border-outline-variant/40 text-tertiary">
                    ~/.kritiq/config.json
                  </div>
                  <p>Session JWT tokens are stored locally after <code className="text-primary">kritiq login</code>. Used automatically for authenticated API calls.</p>
                </div>
              </div>
            </div>
          </div>

          {/* ═══════════ Full Command Reference ═══════════ */}
          <section className="space-y-lg pt-lg border-t border-outline-variant">
            <div className="flex items-center justify-between">
              <h2 className="font-headline-md text-headline-md text-on-surface">Full Command Reference</h2>
              <span className="text-[10px] font-mono text-on-surface-variant opacity-60 uppercase">
                7 registered commands · cli/main.py
              </span>
            </div>

            <div className="space-y-lg">
              {CLI_COMMANDS.map((cmd, idx) => (
                <div
                  key={cmd.name}
                  id={`cmd-${cmd.name}`}
                  className="bg-surface-container border border-outline-variant rounded-xl overflow-hidden hover:border-primary/40 transition-all"
                >
                  {/* Command Header */}
                  <div className="p-md flex items-center justify-between border-b border-outline-variant/40">
                    <div className="flex items-center gap-md">
                      <div className={`w-10 h-10 rounded-lg bg-${cmd.color}-container/20 border border-${cmd.color}/30 flex items-center justify-center`}>
                        <span className={`material-symbols-outlined text-[22px] text-${cmd.color}`}>{cmd.icon}</span>
                      </div>
                      <div>
                        <div className="flex items-center gap-sm">
                          <h3 className="font-headline-md text-body-md font-bold text-on-surface">kritiq {cmd.name}</h3>
                          <span className="text-[10px] px-xs py-0.5 rounded bg-surface-container-high border border-outline-variant/40 text-on-surface-variant font-mono">
                            #{idx + 1}
                          </span>
                        </div>
                        <p className="text-[11px] text-on-surface-variant mt-0.5">{cmd.description}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleSource(cmd.name)}
                      className="text-[10px] text-primary hover:text-primary/80 font-bold flex items-center gap-xs transition-colors"
                    >
                      <span className="material-symbols-outlined text-[14px]">code</span>
                      {showSource[cmd.name] ? 'Hide Source' : 'View Source'}
                    </button>
                  </div>

                  {/* Command Body */}
                  <div className="p-md space-y-md">
                    {/* Usage */}
                    <div className="space-y-xs">
                      <div className="text-[10px] font-label-caps uppercase text-on-surface-variant tracking-wider font-bold">Usage</div>
                      <div className="flex items-center justify-between bg-surface-container-lowest p-xs rounded border border-outline-variant/40 font-mono text-[12px]">
                        <code className="text-tertiary">$ {cmd.usage}</code>
                        <button
                          onClick={() => copyToClipboard(cmd.usage, cmd.name)}
                          className="text-[10px] text-on-surface-variant hover:text-primary transition-colors flex items-center gap-0.5"
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            {copiedCmd === cmd.name ? 'check' : 'content_copy'}
                          </span>
                          {copiedCmd === cmd.name ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                    </div>

                    {/* Options Table */}
                    {cmd.options.length > 0 && (
                      <div className="space-y-xs">
                        <div className="text-[10px] font-label-caps uppercase text-on-surface-variant tracking-wider font-bold">Options</div>
                        <div className="overflow-hidden rounded border border-outline-variant/40">
                          <table className="w-full text-[11px]">
                            <thead>
                              <tr className="bg-surface-container-high text-on-surface-variant">
                                <th className="text-left px-sm py-xs font-label-caps uppercase text-[10px]">Flag</th>
                                <th className="text-left px-sm py-xs font-label-caps uppercase text-[10px]">Type</th>
                                <th className="text-left px-sm py-xs font-label-caps uppercase text-[10px]">Description</th>
                              </tr>
                            </thead>
                            <tbody>
                              {cmd.options.map((opt) => (
                                <tr key={opt.flag} className="border-t border-outline-variant/30">
                                  <td className="px-sm py-xs font-mono text-primary">{opt.flag}</td>
                                  <td className="px-sm py-xs font-mono text-on-surface-variant">{opt.type}</td>
                                  <td className="px-sm py-xs text-on-surface">{opt.desc}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}

                    {/* Example Terminal Output */}
                    <div className="space-y-xs">
                      <div className="text-[10px] font-label-caps uppercase text-on-surface-variant tracking-wider font-bold">Example</div>
                      <div className="bg-[#0d1117] rounded-lg border border-outline-variant/30 overflow-hidden">
                        <div className="flex items-center px-sm py-xs border-b border-outline-variant/20">
                          <div className="flex gap-1">
                            <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]"></div>
                            <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]"></div>
                          </div>
                          <span className="text-[10px] text-[#8b949e] ml-auto font-mono">{cmd.sourceFile}</span>
                        </div>
                        <div className="p-sm font-mono text-[11px] space-y-0.5">
                          <div className="text-[#58a6ff] font-bold">$ {cmd.example.command}</div>
                          {cmd.example.output.map((line, i) => (
                            <div key={i} className={getOutputStyle(line.style)}>
                              {line.text || '\u00A0'}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Notes */}
                    <div className="p-sm bg-surface-container-high/50 border border-outline-variant/30 rounded-lg flex items-start gap-xs">
                      <span className="material-symbols-outlined text-primary text-[14px] mt-0.5">info</span>
                      <p className="text-[11px] text-on-surface-variant leading-relaxed">{cmd.notes}</p>
                    </div>

                    {/* Source Code Snippet (expandable) */}
                    {showSource[cmd.name] && (
                      <div className="space-y-xs animate-in slide-in-from-top-2">
                        <div className="text-[10px] font-label-caps uppercase text-on-surface-variant tracking-wider font-bold flex items-center gap-xs">
                          <span className="material-symbols-outlined text-[12px]">code</span>
                          Source — {cmd.sourceFile}
                        </div>
                        <pre className="bg-[#0d1117] rounded-lg border border-outline-variant/30 p-sm font-mono text-[11px] text-[#c9d1d9] overflow-x-auto whitespace-pre-wrap leading-relaxed">
                          {cmd.sourceSnippet}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Run Instructions */}
          <section className="pt-lg border-t border-outline-variant space-y-md">
            <h2 className="font-headline-md text-headline-md text-on-surface">Running the CLI</h2>

            <div className="grid md:grid-cols-2 gap-lg">
              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                <div className="flex items-center gap-xs text-primary font-bold text-body-md">
                  <span className="material-symbols-outlined text-[18px]">terminal</span>
                  Via Python Module
                </div>
                <div className="bg-surface-container-lowest p-xs rounded font-mono text-[11px] text-tertiary border border-outline-variant/40 space-y-1">
                  <div><span className="text-on-surface-variant"># From kritiq-backend/ directory</span></div>
                  <div>$ python -m cli.main login</div>
                  <div>$ python -m cli.main init</div>
                  <div>$ python -m cli.main review app/main.py</div>
                  <div>$ python -m cli.main diff HEAD~3</div>
                </div>
              </div>

              <div className="p-md bg-surface-container border border-outline-variant rounded-xl space-y-sm">
                <div className="flex items-center gap-xs text-secondary font-bold text-body-md">
                  <span className="material-symbols-outlined text-[18px]">deployed_code</span>
                  Via kritiq.bat (Windows)
                </div>
                <div className="bg-surface-container-lowest p-xs rounded font-mono text-[11px] text-tertiary border border-outline-variant/40 space-y-1">
                  <div><span className="text-on-surface-variant"># Using batch wrapper</span></div>
                  <div>$ kritiq login</div>
                  <div>$ kritiq init</div>
                  <div>$ kritiq review app/main.py</div>
                  <div>$ kritiq translate app.py --to java</div>
                </div>
              </div>
            </div>

            {/* Supported Languages */}
            <div className="p-md bg-surface-container border border-outline-variant rounded-xl">
              <h3 className="font-bold text-body-md text-on-surface flex items-center gap-xs mb-sm">
                <span className="material-symbols-outlined text-tertiary text-[18px]">language</span>
                Supported Languages (Auto-detected)
              </h3>
              <div className="flex flex-wrap gap-sm">
                {['Python', 'JavaScript', 'TypeScript', 'Go', 'Java', 'Rust', 'C/C++', 'Git Patch'].map((lang) => (
                  <span key={lang} className="px-sm py-xs bg-surface-container-high border border-outline-variant/40 rounded text-[11px] font-mono text-on-surface">
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}

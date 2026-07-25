import React from 'react'
import { Link } from 'react-router-dom'
import { RevealItem } from '../hooks/useScrollReveal.jsx'

export default function Landing() {
  return (
    <div className="bg-surface text-on-surface font-sans min-h-screen selection:bg-primary/30">
      {/* Top Header Nav */}
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-margin h-16 bg-surface/80 backdrop-blur-md border-b border-outline-variant">
        <div className="flex flex-col">
          <span className="text-headline-md font-bold text-primary tracking-[0.1em] leading-none">KRITIQ</span>
          <span className="text-[9px] text-on-surface-variant opacity-60 uppercase font-semibold mt-1 tracking-wider">
            CODE REVIEW THAT KNOWS YOUR CODEBASE
          </span>
        </div>

        <nav className="hidden md:flex gap-lg text-body-sm">
          <a href="#features" className="text-on-surface-variant hover:text-primary transition-colors">
            Features
          </a>
          <Link to="/cli" className="text-on-surface-variant hover:text-primary transition-colors">
            CLI
          </Link>
          <a href="#pricing" className="text-on-surface-variant hover:text-primary transition-colors">
            Pricing
          </a>
          <Link to="/cli-docs" className="text-on-surface-variant hover:text-primary transition-colors">
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
            className="bg-primary-container text-on-primary-container px-md py-xs rounded-lg font-bold text-xs hover:brightness-110 active:opacity-80 transition-all shadow-md shadow-primary-container/20"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="pt-16">
        {/* Hero Section */}
        <section className="relative min-h-[85vh] flex flex-col justify-center px-margin overflow-hidden py-xl">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-xl items-center w-full">
            <div className="z-10">
              <RevealItem delay={0}>
                <h1 className="font-display text-display lg:text-[56px] mb-md leading-tight text-on-surface">
                  Code review that <br />
                  <span className="text-primary font-extrabold">actually knows</span> <br />
                  your codebase.
                </h1>
              </RevealItem>

              <RevealItem delay={100}>
                <p className="font-body-lg text-on-surface-variant mb-xl max-w-xl text-sm leading-relaxed">
                  KRITIQ uses Model Context Protocol (MCP) to retrieve deep project context, delivering AI reviews that understand your abstractions, not just your syntax.
                </p>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="flex flex-wrap gap-md">
                  <Link
                    to="/register"
                    className="bg-primary-container text-on-primary-container px-xl py-md rounded-lg font-bold text-body-md flex items-center gap-sm hover:brightness-110 transition-transform shadow-lg shadow-primary-container/20"
                  >
                    Connect GitHub
                  </Link>
                  <Link
                    to="/cli"
                    className="border border-outline-variant text-on-surface px-xl py-md rounded-lg font-bold text-body-md hover:bg-surface-container transition-colors flex items-center gap-sm"
                  >
                    <span className="material-symbols-outlined text-[18px]">terminal</span>
                    Try the CLI
                  </Link>
                </div>
              </RevealItem>
            </div>

            {/* Stylized Mock Code Panel */}
            <RevealItem delay={200} className="w-full">
              <div id="code-demo" className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary to-tertiary opacity-20 blur-xl"></div>
                <div className="relative bg-surface-container rounded-xl border border-outline-variant overflow-hidden code-glow font-mono text-code-sm shadow-2xl">
                  <div className="flex items-center gap-xs px-md py-sm bg-surface-container-high border-b border-outline-variant">
                    <div className="w-3 h-3 rounded-full bg-error/50"></div>
                    <div className="w-3 h-3 rounded-full bg-secondary/50"></div>
                    <div className="w-3 h-3 rounded-full bg-tertiary/50"></div>
                    <span className="ml-sm text-body-sm text-on-surface-variant opacity-60 font-sans">
                      AuthService.ts — KRITIQ AI Review
                    </span>
                  </div>
                  <div className="p-md leading-relaxed">
                    <div className="flex">
                      <span className="w-8 text-on-surface-variant opacity-30 text-right pr-md">12</span>
                      <code className="text-on-surface">
                        <span className="text-primary font-bold">async</span> <span className="text-tertiary">validateSession</span>(token: <span className="text-secondary">string</span>) &#123;
                      </code>
                    </div>
                    <div className="flex relative bg-primary-container/5 py-0.5">
                      <span className="w-8 text-on-surface-variant opacity-30 text-right pr-md flex items-center justify-end">
                        <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
                      </span>
                      <code className="text-on-surface">
                        &nbsp;&nbsp;<span className="text-primary">const</span> user = <span className="text-primary">await</span> <span className="text-secondary">db</span>.users.findUnique(&#123;
                      </code>
                    </div>

                    {/* Floating AI Comment Card */}
                    <div className="ml-10 my-sm p-md bg-primary-container/10 border border-primary/30 rounded-lg">
                      <div className="flex items-center gap-sm mb-xs">
                        <span className="text-primary font-bold text-body-sm flex items-center gap-xs font-sans">
                          <span className="material-symbols-outlined text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                            auto_awesome
                          </span>
                          KRITIQ AI
                        </span>
                        <span className="text-on-surface-variant opacity-60 text-[10px] font-sans">JUST NOW</span>
                      </div>
                      <p className="text-body-sm text-on-primary-container font-sans">
                        I noticed you're using <code className="bg-primary/20 px-1 rounded font-mono">findUnique</code>. Given the cache policy in <code className="text-tertiary font-mono">redis.config.ts</code>, should we implement a wrap-around here?
                      </p>
                    </div>

                    <div className="flex">
                      <span className="w-8 text-on-surface-variant opacity-30 text-right pr-md">14</span>
                      <code className="text-on-surface">&nbsp;&nbsp;&nbsp;&nbsp;where: &#123; token &#125;</code>
                    </div>
                    <div className="flex">
                      <span className="w-8 text-on-surface-variant opacity-30 text-right pr-md">15</span>
                      <code className="text-on-surface">&nbsp;&nbsp;&#125;);</code>
                    </div>
                  </div>
                </div>
              </div>
            </RevealItem>
          </div>
        </section>

        {/* Trust Strip */}
        <div id="stack" className="py-xl border-y border-outline-variant bg-surface-container-low overflow-hidden">
          <RevealItem delay={100}>
            <div className="max-w-7xl mx-auto px-margin flex flex-wrap justify-center items-center gap-xl text-on-surface-variant">
              <span className="text-label-caps font-label-caps tracking-[0.2em]">BUILT WITH</span>
              <div className="flex items-center gap-xs font-bold text-body-md text-primary">
                <span className="material-symbols-outlined text-[20px]">brightness_7</span> Google Gemini
              </div>
              <div className="w-px h-5 bg-outline-variant"></div>
              <div className="flex items-center gap-xs font-bold text-body-md text-secondary">
                <span className="material-symbols-outlined text-[20px]">hub</span> MCP Context
              </div>
              <div className="w-px h-5 bg-outline-variant"></div>
              <div className="flex items-center gap-xs font-bold text-body-md text-tertiary">
                <span className="material-symbols-outlined text-[20px]">layers</span> MongoDB Atlas
              </div>
            </div>
          </RevealItem>
        </div>

        {/* Section 1: Why generic AI fails developers */}
        <section className="py-xl px-margin">
          <div className="max-w-7xl mx-auto">
            <RevealItem delay={0}>
              <h2 className="text-display font-display lg:text-[40px] mb-xl text-center text-on-surface">
                Why generic AI fails developers.
              </h2>
            </RevealItem>

            <div className="grid md:grid-cols-3 gap-lg">
              <RevealItem delay={100}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-colors group h-full">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-md group-hover:scale-110 transition-transform">
                    <span className="material-symbols-outlined text-primary">layers</span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-xs text-on-surface">Manual review doesn't scale</h3>
                  <p className="text-on-surface-variant text-body-md">
                    Senior engineers spend 30% of their time unblocking others. KRITIQ acts as the first line of defense.
                  </p>
                </div>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-colors group h-full">
                  <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center mb-md group-hover:scale-110 transition-transform">
                    <span className="material-symbols-outlined text-secondary">visibility_off</span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-xs text-on-surface">AI tools only see one file</h3>
                  <p className="text-on-surface-variant text-body-md">
                    Most LLMs lack the context of your entire architecture. They suggest fixes that break dependencies elsewhere.
                  </p>
                </div>
              </RevealItem>

              <RevealItem delay={300}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl hover:border-primary transition-colors group h-full">
                  <div className="w-10 h-10 rounded-lg bg-tertiary/10 flex items-center justify-center mb-md group-hover:scale-110 transition-transform">
                    <span className="material-symbols-outlined text-tertiary">code_blocks</span>
                  </div>
                  <h3 className="font-headline-md text-headline-md mb-xs text-on-surface">Porting code is risky</h3>
                  <p className="text-on-surface-variant text-body-md">
                    Translating logic between languages often loses semantic meaning. KRITIQ preserves context across stacks.
                  </p>
                </div>
              </RevealItem>
            </div>
          </div>
        </section>

        {/* Section 2: How KRITIQ is different (Pipeline Flow) */}
        <section className="py-xl px-margin bg-surface-container-low/50 border-y border-outline-variant">
          <div className="max-w-7xl mx-auto">
            <RevealItem delay={0}>
              <h2 className="text-display font-display lg:text-[40px] mb-xl text-center text-on-surface">
                How KRITIQ is different
              </h2>
            </RevealItem>

            {/* Pipeline Flow Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-md relative">
              <RevealItem delay={100}>
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl text-center space-y-xs relative">
                  <span className="material-symbols-outlined text-primary text-[24px]">folder_open</span>
                  <h4 className="font-bold text-body-md text-on-surface">Your Repo</h4>
                  <p className="font-label-caps text-[9px] uppercase text-on-surface-variant">SOURCE</p>
                </div>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl text-center space-y-xs relative">
                  <span className="material-symbols-outlined text-secondary text-[24px]">hub</span>
                  <h4 className="font-bold text-body-md text-on-surface">MCP Context</h4>
                  <p className="font-label-caps text-[9px] uppercase text-on-surface-variant">RETRIEVAL</p>
                </div>
              </RevealItem>

              {/* Highlighted Gemini + RAG Step */}
              <RevealItem delay={300}>
                <div className="p-md bg-primary-container border border-primary rounded-xl text-center space-y-xs text-on-primary-container shadow-lg shadow-primary-container/30">
                  <span className="material-symbols-outlined text-[24px]">auto_awesome</span>
                  <h4 className="font-bold text-body-md">Gemini + RAG</h4>
                  <p className="font-label-caps text-[9px] uppercase opacity-80">CURATED REVIEW DATASET</p>
                </div>
              </RevealItem>

              <RevealItem delay={400}>
                <div className="p-md bg-surface-container border border-outline-variant rounded-xl text-center space-y-xs relative">
                  <span className="material-symbols-outlined text-tertiary text-[24px]">check_circle</span>
                  <h4 className="font-bold text-body-md text-on-surface">Review / Translation</h4>
                  <p className="font-label-caps text-[9px] uppercase text-on-surface-variant">OUTPUT FLOW</p>
                </div>
              </RevealItem>
            </div>
          </div>
        </section>

        {/* Section 3: Bento Grid Layout */}
        <section id="features" className="py-xl px-margin">
          <div className="max-w-7xl mx-auto space-y-lg">
            {/* Row 1: Large Cards */}
            <div className="grid md:grid-cols-2 gap-lg">
              <RevealItem delay={100}>
                <div className="p-xl bg-surface-container border border-outline-variant rounded-xl space-y-md min-h-[220px] flex flex-col justify-between hover:border-primary transition-colors">
                  <div>
                    <h3 className="font-headline-lg text-headline-lg text-on-surface mb-xs">Context-aware Code Review</h3>
                    <p className="text-on-surface-variant text-body-md">
                      KRITIQ reads your entire dependency graph to spot logical errors that single-file linters miss.
                    </p>
                  </div>
                  <div className="flex justify-end">
                    <span className="material-symbols-outlined text-[56px] text-outline-variant opacity-40">analytics</span>
                  </div>
                </div>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="p-xl bg-surface-container border border-outline-variant rounded-xl space-y-md min-h-[220px] flex flex-col justify-between hover:border-primary transition-colors">
                  <div>
                    <h3 className="font-headline-lg text-headline-lg text-on-surface mb-xs">Cross-language Translation</h3>
                    <p className="text-on-surface-variant text-body-md">
                      Port Python to Rust or Go to TypeScript while maintaining business logic.
                    </p>
                  </div>
                  <div className="flex justify-end">
                    <span className="material-symbols-outlined text-[56px] text-tertiary/40">translate</span>
                  </div>
                </div>
              </RevealItem>
            </div>

            {/* Row 2: Medium Cards */}
            <div className="grid md:grid-cols-2 gap-lg">
              <RevealItem delay={100}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl space-y-xs hover:border-primary transition-colors">
                  <span className="material-symbols-outlined text-primary text-[28px] mb-xs">forum</span>
                  <h4 className="font-headline-md text-headline-md text-on-surface">Plain-language Explanations</h4>
                  <p className="text-on-surface-variant text-body-md">
                    Get executive summaries of complex diffs for non-technical stakeholders.
                  </p>
                </div>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl space-y-xs hover:border-primary transition-colors">
                  <span className="material-symbols-outlined text-secondary text-[28px] mb-xs">hub</span>
                  <h4 className="font-headline-md text-headline-md text-on-surface">GitHub Integration</h4>
                  <p className="text-on-surface-variant text-body-md">
                    Native PR comments, check runs, and automated review status directly in your workflow.
                  </p>
                </div>
              </RevealItem>
            </div>

            {/* Row 3: Wide Cards */}
            <div className="grid md:grid-cols-2 gap-lg">
              <RevealItem delay={100}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl space-y-sm hover:border-primary transition-colors">
                  <h4 className="font-headline-md text-headline-md text-on-surface">Review History &amp; Dashboard</h4>
                  <p className="text-on-surface-variant text-body-md">
                    Track codebase quality trends and common architectural code smells across your organization.
                  </p>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full w-[70%] rounded-full"></div>
                  </div>
                </div>
              </RevealItem>

              <RevealItem delay={200}>
                <div className="p-lg bg-surface-container border border-outline-variant rounded-xl space-y-sm hover:border-primary transition-colors">
                  <div className="flex justify-between items-center">
                    <h4 className="font-headline-md text-headline-md text-on-surface">CLI + Web</h4>
                    <div className="flex gap-xs">
                      <span className="px-xs py-0.5 rounded text-[9px] font-label-caps uppercase bg-tertiary-container text-on-tertiary-container">
                        STABLE
                      </span>
                      <span className="px-xs py-0.5 rounded text-[9px] font-label-caps uppercase bg-secondary-container text-on-secondary-container">
                        CROSS-PLATFORM
                      </span>
                    </div>
                  </div>
                  <p className="text-on-surface-variant text-body-md">
                    Review locally before pushing, or manage everything from our high-performance web dashboard.
                  </p>
                </div>
              </RevealItem>
            </div>
          </div>
        </section>

        {/* Section 4: Power in every environment */}
        <section className="py-xl px-margin bg-surface-container-low border-t border-outline-variant">
          <div className="max-w-7xl mx-auto space-y-xl">
            <RevealItem delay={0}>
              <h2 className="text-display font-display lg:text-[40px] text-center text-on-surface">
                Power in every environment.
              </h2>
            </RevealItem>

            <div className="grid md:grid-cols-2 gap-xl">
              {/* Web Dashboard Side */}
              <RevealItem delay={100}>
                <div className="space-y-md">
                  <div className="flex items-center gap-xs text-primary font-bold text-headline-md">
                    <span className="material-symbols-outlined">dashboard</span>
                    Web Dashboard
                  </div>
                  
                  {/* Mock Screenshot Card */}
                  <div className="bg-surface-container rounded-xl border border-outline-variant p-md space-y-md shadow-2xl">
                    <div className="flex items-center justify-between border-b border-outline-variant/40 pb-sm">
                      <div className="flex items-center gap-xs">
                        <div className="w-2.5 h-2.5 rounded-full bg-error/60"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-secondary/60"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-tertiary/60"></div>
                      </div>
                      <span className="text-[10px] font-mono text-on-surface-variant opacity-60">kritiq.dev/dashboard</span>
                    </div>

                    <div className="grid grid-cols-2 gap-sm text-[11px]">
                      <div className="p-xs bg-surface-container-high rounded border border-outline-variant/30">
                        <p className="text-[9px] text-on-surface-variant uppercase">Codebase Health</p>
                        <p className="font-bold text-tertiary text-sm">98.4%</p>
                      </div>
                      <div className="p-xs bg-surface-container-high rounded border border-outline-variant/30">
                        <p className="text-[9px] text-on-surface-variant uppercase">Critical Vulns</p>
                        <p className="font-bold text-error text-sm">0 Found</p>
                      </div>
                    </div>
                  </div>

                  <p className="text-on-surface-variant text-xs leading-relaxed">
                    Manage organization-wide policies, view historical insights, and handle deep-dive architectural reviews in a rich visual environment.
                  </p>
                </div>
              </RevealItem>

              {/* CLI Tool Side */}
              <RevealItem delay={200}>
                <div className="space-y-md">
                  <div className="flex items-center gap-xs text-tertiary font-bold text-headline-md">
                    <span className="material-symbols-outlined">terminal</span>
                    CLI Tool
                  </div>

                  {/* Terminal Mockup Card */}
                  <div className="bg-surface-container rounded-xl border border-outline-variant p-md font-mono text-code-sm leading-relaxed text-[11px] space-y-xs shadow-2xl">
                    <div className="text-tertiary font-bold">$ kritiq review .</div>
                    <div className="text-on-surface-variant">Justifying codebase with MCP Context...</div>
                    <div className="text-on-surface-variant">Found 12 files for review.</div>
                    <div className="text-error pt-xs">[CRITICAL] API key exposure in app.example</div>
                    <div className="text-secondary">[INFO] 3 potential N+1 query code smells in scheduler.py</div>
                    <div className="text-tertiary pt-xs">Analysis complete: 2 warnings, 1 error.</div>
                    <div className="flex items-center gap-xs pt-xs">
                      <span className="text-tertiary">$</span>
                      <span className="w-2 h-4 bg-on-surface inline-block animate-pulse"></span>
                    </div>
                  </div>

                  <p className="text-on-surface-variant text-xs leading-relaxed">
                    Run local reviews as part of your pre-commit hooks. Get instant feedback without leaving your terminal or switching contexts.
                  </p>
                </div>
              </RevealItem>
            </div>
          </div>
        </section>

        {/* Section 5: Ready for a better review process? */}
        <section className="py-2xl px-margin text-center bg-surface">
          <div className="max-w-3xl mx-auto space-y-md py-xl">
            <RevealItem delay={0}>
              <h2 className="font-display text-display lg:text-[44px] text-on-surface">
                Ready for a better review process?
              </h2>
            </RevealItem>

            <RevealItem delay={100}>
              <p className="font-body-lg text-on-surface-variant text-sm">
                Join 500+ engineering teams using KRITIQ to ship faster with fewer bugs.
              </p>
            </RevealItem>

            <RevealItem delay={200}>
              <div className="flex justify-center gap-md pt-md">
                <Link
                  to="/register"
                  className="bg-primary-container text-on-primary-container px-xl py-md rounded-lg font-bold text-body-md hover:brightness-110 transition-transform shadow-lg shadow-primary-container/30"
                >
                  Get Started Free
                </Link>
                <Link
                  to="/cli"
                  className="border border-outline-variant text-on-surface px-xl py-md rounded-lg font-bold text-body-md hover:bg-surface-container transition-colors"
                >
                  Schedule Demo
                </Link>
              </div>
            </RevealItem>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-outline-variant py-lg px-margin text-center text-on-surface-variant text-body-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-md text-xs">
          <div>
            <span className="font-bold text-primary font-display tracking-widest mr-2">KRITIQ AI</span>
            <span>© 2026 KRITIQ AI. Built for high-performance engineering.</span>
          </div>
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

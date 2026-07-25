import React from 'react'

export default function NavBar({ title, actionButton }) {
  return (
    <header className="fixed top-0 right-0 left-64 h-16 border-b border-outline-variant bg-surface/90 backdrop-blur-md flex items-center justify-between px-lg z-40">
      <div className="flex items-center flex-1 max-w-xl gap-md">
        {title ? (
          <h2 className="font-headline-md text-headline-md text-on-surface truncate">{title}</h2>
        ) : (
          <div className="relative w-full group">
            <span className="material-symbols-outlined absolute left-md top-1/2 -translate-y-1/2 text-outline group-focus-within:text-primary text-[18px]">
              search
            </span>
            <input
              className="w-full bg-surface-container-low border border-outline-variant rounded-lg pl-10 pr-md py-xs font-body-md text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary transition-all text-xs"
              placeholder="Search repositories, reviews, translations..."
              type="text"
            />
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-lg">
        <a
          href="https://github.com/octocat/Hello-World"
          target="_blank"
          rel="noreferrer"
          className="font-body-md text-body-sm text-on-surface-variant hover:text-primary transition-colors cursor-pointer"
        >
          Docs
        </a>
        <div className="flex items-center gap-sm">
          <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer p-xs text-[20px]" title="Notifications">
            notifications
          </button>
          <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors cursor-pointer p-xs text-[20px]" title="Help">
            help_outline
          </button>
        </div>
        {actionButton}
      </div>
    </header>
  )
}

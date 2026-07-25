import React, { useMemo, useState } from 'react'

function buildTree(filePaths) {
  const root = { name: '', children: {}, isFolder: true }
  for (const rawPath of filePaths || []) {
    if (!rawPath) continue
    const segments = rawPath.split('/').filter(Boolean)
    let cursor = root
    segments.forEach((seg, idx) => {
      const isLeaf = idx === segments.length - 1
      if (!cursor.children[seg]) {
        cursor.children[seg] = {
          name: seg,
          children: isLeaf ? null : {},
          isFolder: !isLeaf,
          path: segments.slice(0, idx + 1).join('/')
        }
      } else if (!isLeaf && !cursor.children[seg].isFolder) {
        cursor.children[seg].isFolder = true
        cursor.children[seg].children = cursor.children[seg].children || {}
      }
      cursor = cursor.children[seg]
    })
  }
  return root
}

function sortEntries(entries) {
  return entries.slice().sort((a, b) => {
    if (a.isFolder !== b.isFolder) return a.isFolder ? -1 : 1
    return a.name.localeCompare(b.name)
  })
}

function TreeNode({ node, depth, selectedPath, onSelectFile, expandedSet, toggleExpand, renderFileActions }) {
  const isSelected = selectedPath === node.path
  const entries = node.children ? sortEntries(Object.values(node.children)) : []
  const isExpanded = expandedSet.has(node.path)

  return (
    <div>
      {node.path && (
        <div
          className={`flex items-center gap-xs px-sm py-1 rounded transition-colors font-mono text-code-sm text-xs ${
            isSelected
              ? 'bg-primary/15 ring-1 ring-primary/50'
              : node.isFolder
              ? 'hover:bg-surface-container-high'
              : 'hover:bg-surface-container-high'
          }`}
          style={{ paddingLeft: 8 + depth * 16 }}
        >
          <div
            onClick={() => {
              if (node.isFolder) {
                toggleExpand(node.path)
              } else {
                onSelectFile?.(node.path)
              }
            }}
            className={`flex items-center gap-xs flex-1 min-w-0 cursor-pointer ${
              isSelected
                ? 'text-primary'
                : node.isFolder
                ? 'text-on-surface'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[16px]" style={{ width: 16, flexShrink: 0 }}>
              {node.isFolder
                ? isExpanded
                  ? 'folder_open'
                  : 'folder'
                : 'insert_drive_file'}
            </span>
            <span className="truncate">{node.name}</span>
          </div>
          {!node.isFolder && renderFileActions && (
            <div className="flex items-center gap-xs flex-shrink-0 pl-xs">
              {renderFileActions(node.path)}
            </div>
          )}
        </div>
      )}
      {node.isFolder && entries.length > 0 && (
        <div className={isExpanded || !node.path ? '' : 'hidden'}>
          {entries.map((entry) => (
            <TreeNode
              key={entry.path}
              node={entry}
              depth={depth + (node.path ? 1 : 0)}
              selectedPath={selectedPath}
              onSelectFile={onSelectFile}
              expandedSet={expandedSet}
              toggleExpand={toggleExpand}
              renderFileActions={renderFileActions}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function RepoFilePicker({
  files,
  selectedPath,
  onSelectFile,
  placeholder = '-- Pick a file --',
  loading = false,
  loadingText = 'Indexing repository files...',
  emptyText = 'No files found in this repository.',
  labelIcon = 'insert_drive_file',
  labelText = 'Repository File',
  renderFileActions = null
}) {
  const tree = useMemo(() => buildTree(files), [files])
  const fileCount = useMemo(() => (files || []).length, [files])
  const folderCount = useMemo(() => {
    let count = 0
    const walk = (node) => {
      if (!node.children) return
      Object.values(node.children).forEach((c) => {
        if (c.isFolder) {
          count += 1
          walk(c)
        }
      })
    }
    walk(tree)
    return count
  }, [tree])

  const defaultExpanded = useMemo(() => {
    const s = new Set()
    if (selectedPath) {
      const segs = selectedPath.split('/').filter(Boolean)
      let acc = ''
      for (let i = 0; i < segs.length - 1; i += 1) {
        acc = acc ? acc + '/' + segs[i] : segs[i]
        s.add(acc)
      }
    }
    return s
  }, [selectedPath])

  const [expandedSet, setExpandedSet] = useState(defaultExpanded)
  const [query, setQuery] = useState('')

  const filteredFiles = useMemo(() => {
    if (!query.trim()) return null
    const q = query.trim().toLowerCase()
    return (files || []).filter((f) => f.toLowerCase().includes(q))
  }, [files, query])

  const toggleExpand = (path) => {
    setExpandedSet((prev) => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }

  const expandAll = () => {
    const all = new Set()
    const walk = (node) => {
      if (!node.children) return
      Object.values(node.children).forEach((c) => {
        if (c.isFolder) {
          all.add(c.path)
          walk(c)
        }
      })
    }
    walk(tree)
    setExpandedSet(all)
  }
  const collapseAll = () => setExpandedSet(new Set())

  const displayTree = useMemo(() => {
    if (filteredFiles) return buildTree(filteredFiles)
    return tree
  }, [filteredFiles, tree])

  if (loading) {
    return (
      <div className="w-full max-w-full">
        <div className="flex items-center gap-xs px-xs py-1 text-on-surface-variant text-[11px] font-mono">
          <span className="material-symbols-outlined text-[16px] animate-spin">refresh</span>
          {loadingText}
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-full">
      <div className="flex items-center justify-between gap-xs px-xs py-1">
        <div className="flex items-center gap-xs text-[10px] font-label-caps uppercase text-on-surface-variant">
          <span className="material-symbols-outlined text-[14px]">{labelIcon}</span>
          {labelText}
          <span className="text-outline/70">
            ({fileCount} file{fileCount === 1 ? '' : 's'}
            {folderCount ? `, ${folderCount} folder${folderCount === 1 ? '' : 's'}` : ''})
          </span>
        </div>
        {(files || []).length > 0 && (
          <div className="flex items-center gap-xs">
            <button
              type="button"
              onClick={expandAll}
              className="text-[10px] text-primary hover:underline font-bold"
            >
              Expand all
            </button>
            <span className="text-outline/60 text-[10px]">|</span>
            <button
              type="button"
              onClick={collapseAll}
              className="text-[10px] text-primary hover:underline font-bold"
            >
              Collapse
            </button>
          </div>
        )}
      </div>

      {(files || []).length > 0 && (
        <div className="px-xs pb-xs">
          <div className="relative group">
            <span className="material-symbols-outlined absolute left-xs top-1/2 -translate-y-1/2 text-outline text-[14px]">
              search
            </span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter files by name or path..."
              className="w-full bg-surface-container-lowest border border-outline-variant rounded px-lg py-1 font-mono text-code-sm text-on-surface placeholder:text-outline/60 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-xs"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="material-symbols-outlined absolute right-xs top-1/2 -translate-y-1/2 text-outline hover:text-on-surface text-[14px]"
                title="Clear filter"
              >
                close
              </button>
            )}
          </div>
          {filteredFiles && (
            <div className="text-[10px] font-mono text-on-surface-variant pt-1">
              Showing {filteredFiles.length} of {fileCount} files
            </div>
          )}
        </div>
      )}

      <div className="max-h-72 overflow-y-auto rounded-lg border border-outline-variant bg-surface-container-lowest py-xs">
        {(files || []).length === 0 ? (
          <div className="px-sm py-lg text-center text-on-surface-variant font-body-sm text-xs">
            {emptyText}
          </div>
        ) : filteredFiles && filteredFiles.length === 0 ? (
          <div className="px-sm py-md text-center text-on-surface-variant font-mono text-xs">
            No files match &quot;{query}&quot;.
          </div>
        ) : (
          <TreeNode
            node={displayTree}
            depth={0}
            selectedPath={selectedPath}
            onSelectFile={onSelectFile}
            expandedSet={expandedSet}
            toggleExpand={toggleExpand}
            renderFileActions={renderFileActions}
          />
        )}
      </div>

      {selectedPath && !renderFileActions && (
        <div className="mt-xs px-xs py-1 rounded bg-primary/10 border border-primary/30 flex items-center gap-xs">
          <span className="material-symbols-outlined text-primary text-[14px]">task_alt</span>
          <span className="text-[11px] font-mono text-primary truncate" title={selectedPath}>
            Selected: {selectedPath}
          </span>
        </div>
      )}
    </div>
  )
}

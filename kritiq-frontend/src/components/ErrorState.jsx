import React from 'react'

// Dev domain - Error state component stub
export default function ErrorState({ error }) {
  return <div className="text-center text-red-500 p-8">Error: {error || 'Something went wrong.'}</div>
}

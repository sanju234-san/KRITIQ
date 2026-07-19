# Release Notes — KRITIQ Backend v1.0.0

We are pleased to announce the first production-ready release of the KRITIQ Backend Core, housing the APIs, database layers, security, session auth, and asynchronous AI routing handlers.

---

## Features Included

1. **Authentication & Identity**:
   * Secure user registration, validation, and login matching hashed credentials.
   * Session authorization verified via cryptographically signed JWT tokens.
2. **AI Integration Handlers**:
   * Synchronous offloaded endpoints supporting AI Code Review, Translation, and Explanation requests.
   * RAG pipeline integration for custom context inclusion.
3. **Database Repository Layer**:
   * Reused MongoClient singleton connection mapping collections.
   * Automated index verification (`email_1` index for users).
   * Sorted activity logging for user history.
4. **Backend Security & Middlewares**:
   * Request Payload Size Limiting (capped at 1MB to prevent overload).
   * In-memory Rate Limiting (60 requests/minute per client IP).
   * Hardened HTTP Security Headers.

---

## Performance Optimizations & Fixes

* **Thread Pool Offloading**: Offloaded slow synchronous AI service layers to non-blocking threads to keep the main event loop free.
* **Warning Cleanups**: Removed JWT Secret strength warnings by upgrading to 32-byte keys.
* **Starlette Code deprecations**: Cleared HTTP status code deprecations from routing parameters.
* **Isolated Testing Rate Limiter Cache**: Automatically resets rate-limiter caches in playground scripts to prevent self-rate-limiting.

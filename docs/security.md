# Security & OWASP ASVS Verification Checklist

## 1. Authentication & Session Security (ASVS V2 / V3)
- **Password Storage**: Passwords are hashed using `node:crypto` `scryptSync` with a unique 16-byte cryptographic salt per user (`apps/api/src/auth.ts`). Verification uses `timingSafeEqual` to prevent timing side-channel attacks.
- **Token & API Key Storage**: Session tokens (`vls_…`) and API keys (`vlk_…`) are never stored in plaintext; only their `SHA-256` hex digests (`token_hash`, `key_hash`) are persisted in PostgreSQL.
- **Log Redaction**: Pino logger is configured with `redact: ["req.headers.authorization", "req.headers.cookie", "req.headers['x-api-key']"]`.

## 2. Access Control & Multi-Tenant Isolation (ASVS V4)
- **Query-Level Tenant Isolation**: Every tenant table (`projects`, `media`, `analyses`, `frame_events`, `tracks`, `zones`, `alerts`, `datasets`, `annotations`, `training_runs`, `models`, `api_keys`, `audit_logs`) carries a non-null `org_id` column, and every SELECT/UPDATE query filters on `eq(table.orgId, ctx.orgId)`.
- **Hierarchical RBAC**: Enforced via `requireRole(db, minRole)` across `owner > admin > member > viewer`. Verified in automated tests (`apps/api/src/app.test.ts`).

## 3. Input Validation, Uploads & Rate Limiting (ASVS V5 / V12)
- **Schema Validation**: All request bodies are validated with `Zod` v4 prior to database or queue execution.
- **Upload Hardening**: Presigned S3 upload requests enforce a strict MIME allowlist (`image/jpeg`, `image/png`, `image/webp`, `video/mp4`, `video/webm`, `video/quicktime`), a 2 GiB size cap, filename sanitization, and magic-byte header verification (`verifyMagicBytes`).
- **Headers & Rate Limiting**: `@fastify/helmet`, strict origin allowlist via `@fastify/cors`, and `@fastify/rate-limit` (`300 req/min`).

## 4. Privacy & GDPR Controls
- **Privacy Redaction Mode**: Enabled by default on projects and the Analyze workspace; redacts upper-head / face regions on the canvas overlay and before frame export.
- **Cascading Tenant Deletion**: All foreign keys reference `orgs(id) ON DELETE CASCADE`, enabling complete tenant data erasure.

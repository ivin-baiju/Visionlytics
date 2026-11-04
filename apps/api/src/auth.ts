import { createHash, randomBytes, scryptSync, timingSafeEqual } from "node:crypto";
import type { FastifyReply, FastifyRequest } from "fastify";
import { and, eq, gt, isNull } from "drizzle-orm";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "./db/schema.ts";

export type Role = "owner" | "admin" | "member" | "viewer";

const ROLE_WEIGHT: Record<Role, number> = {
  viewer: 1,
  member: 2,
  admin: 3,
  owner: 4,
};

export interface AuthContext {
  userId: string | null;
  orgId: string;
  role: Role;
  via: "session" | "api_key";
}

export function hashPassword(password: string, salt = randomBytes(16).toString("hex")): {
  hash: string;
  salt: string;
} {
  const derived = scryptSync(password, salt, 64).toString("hex");
  return { hash: derived, salt };
}

export function verifyPassword(password: string, hash: string, salt: string): boolean {
  const derived = scryptSync(password, salt, 64);
  const expected = Buffer.from(hash, "hex");
  if (derived.length !== expected.length) return false;
  return timingSafeEqual(derived, expected);
}

export function sha256Hex(raw: string): string {
  return createHash("sha256").update(raw).digest("hex");
}

export function generateSessionToken(): { raw: string; hash: string } {
  const raw = `vls_${randomBytes(24).toString("hex")}`;
  return { raw, hash: sha256Hex(raw) };
}

export function generateApiKey(): { raw: string; prefix: string; hash: string } {
  const secret = randomBytes(24).toString("hex");
  const raw = `vlk_${secret}`;
  return {
    raw,
    prefix: raw.slice(0, 12),
    hash: sha256Hex(raw),
  };
}

export function hasMinimumRole(actual: Role, required: Role): boolean {
  return ROLE_WEIGHT[actual] >= ROLE_WEIGHT[required];
}

export async function resolveAuth(
  req: FastifyRequest,
  db: PostgresJsDatabase<typeof schema>,
): Promise<AuthContext | null> {
  const apiKeyHeader = req.headers["x-api-key"];
  if (typeof apiKeyHeader === "string" && apiKeyHeader.startsWith("vlk_")) {
    const hash = sha256Hex(apiKeyHeader);
    const [keyRow] = await db
      .select()
      .from(schema.apiKeys)
      .where(and(eq(schema.apiKeys.keyHash, hash), isNull(schema.apiKeys.revokedAt)))
      .limit(1);
    if (!keyRow) return null;
    await db
      .update(schema.apiKeys)
      .set({ lastUsedAt: new Date() })
      .where(eq(schema.apiKeys.id, keyRow.id));
    return {
      userId: null,
      orgId: keyRow.orgId,
      role: keyRow.role,
      via: "api_key",
    };
  }

  const authHeader = req.headers.authorization;
  if (typeof authHeader === "string" && authHeader.startsWith("Bearer ")) {
    const raw = authHeader.slice("Bearer ".length).trim();
    const hash = sha256Hex(raw);
    const [sess] = await db
      .select()
      .from(schema.sessions)
      .where(and(eq(schema.sessions.tokenHash, hash), gt(schema.sessions.expiresAt, new Date())))
      .limit(1);
    if (!sess) return null;
    const [membership] = await db
      .select()
      .from(schema.orgMembers)
      .where(
        and(
          eq(schema.orgMembers.orgId, sess.orgId),
          eq(schema.orgMembers.userId, sess.userId),
        ),
      )
      .limit(1);
    if (!membership) return null;
    return {
      userId: sess.userId,
      orgId: sess.orgId,
      role: membership.role,
      via: "session",
    };
  }

  return null;
}

export function requireRole(
  db: PostgresJsDatabase<typeof schema>,
  minRole: Role,
): (req: FastifyRequest, reply: FastifyReply) => Promise<AuthContext | undefined> {
  return async (req, reply) => {
    const ctx = await resolveAuth(req, db);
    if (!ctx) {
      reply.code(401).send({ error: "Authentication required" });
      return undefined;
    }
    if (!hasMinimumRole(ctx.role, minRole)) {
      reply.code(403).send({
        error: `Insufficient role: requires ${minRole}, current role is ${ctx.role}`,
      });
      return undefined;
    }
    return ctx;
  };
}

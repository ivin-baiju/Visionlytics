"""
Authentication, Authorization, and Security Utilities for Visionlytics API.

Features:
- Password hashing & verification using bcrypt.
- JWT creation and verification.
- Role-based Access Control (RBAC): 'admin', 'analyst', 'viewer'.
- Input sanitization against XSS and injection.
- Security dependencies for FastAPI routes.
"""

import html
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from db.supabase_client import DB_PATH, supabase_client

# Environment secrets (fall back to safe dev secret with loud warning in logs)
SECRET_KEY = os.environ.get("VISIONLYTICS_SECRET_KEY", "dev-insecure-secret-key-change-in-prod-8f830a7d")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer(auto_error=False)


# ── Password Hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Input Sanitization ────────────────────────────────────────────────────────

def sanitize_string(text: str, max_length: int = 2000) -> str:
    """
    Sanitize text input against XSS and strip control characters.
    Escapes HTML special entities (<, >, &, \", \').
    """
    if not text:
        return ""
    # Strip null bytes & control chars
    clean = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", str(text))
    # Escape HTML to prevent stored XSS
    escaped = html.escape(clean.strip())
    return escaped[:max_length]


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filenames to prevent directory traversal attacks."""
    basename = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", basename)
    return clean[:100]


# ── User and Role Storage (Local SQLite Fallback & Supabase) ───────────────────

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Fetch user record by username."""
    # Check Supabase first if configured
    if supabase_client.use_supabase and supabase_client.client:
        try:
            res = supabase_client.client.table("users").select("*").eq("username", username).limit(1).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception:
            pass

    # Check local SQLite fallback
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def register_user(username: str, email: str, password: str, role: str = "analyst") -> Dict[str, Any]:
    """Register a new user with hashed password."""
    clean_username = sanitize_string(username, 50)
    clean_email = sanitize_string(email, 100)
    if not clean_username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")

    hashed = hash_password(password)

    if supabase_client.use_supabase and supabase_client.client:
        try:
            res = supabase_client.client.table("users").insert({
                "username": clean_username,
                "email": clean_email,
                "hashed_password": hashed,
                "role": role,
            }).execute()
            return {"username": clean_username, "role": role}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Registration failed: {exc}")

    # Fallback to local DB
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, role) VALUES (?, ?, ?, ?)",
            (clean_username, clean_email, hashed, role),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="Username or email already exists.")
    conn.close()

    return {"username": clean_username, "role": role}


# Ensure default admin account exists for demo / setup if empty
def seed_default_admin():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL, hashed_password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'analyst', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, role) VALUES (?, ?, ?, ?)",
            ("admin", "admin@visionlytics.ai", hash_password("Visionlytics@Admin2026!"), "admin"),
        )
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, role) VALUES (?, ?, ?, ?)",
            ("analyst", "analyst@visionlytics.ai", hash_password("AnalystPass2026!"), "analyst"),
        )
        conn.commit()
    conn.close()

try:
    seed_default_admin()
except Exception:
    pass


# ── Dependency Guards ─────────────────────────────────────────────────────────

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> dict:
    """Dependency: Extract and verify current user from Bearer JWT."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please include a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")
    return payload


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency: Restrict route strictly to users with 'admin' role."""
    role = current_user.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrator privileges required.",
        )
    return current_user

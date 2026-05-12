#!/usr/bin/env python3
"""Idempotent LibreChat user bootstrap.

Inserts a `users` document directly into MongoDB with a bcrypt-hashed password.
Mirrors what LibreChat's `AuthService.registerUser` does for local-provider
users (bcrypt rounds=10, role='USER', provider='local', emailVerified=true).

Avoids pulling the full LibreChat image just to run `npm run create-user`.

Env:
  MONGO_URI               (default: mongodb://mongodb:27017/LibreChat)
  LIBRECHAT_EMAIL         (required)
  LIBRECHAT_PASSWORD      (required, >= 8 chars)
  LIBRECHAT_USER_NAME     (default: Syncer)
  LIBRECHAT_USER_USERNAME (default: syncer)
"""
import os
import sys
import time
from datetime import datetime, timezone

import bcrypt
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/LibreChat")
EMAIL = (os.environ.get("LIBRECHAT_EMAIL") or "").strip().lower()
PASSWORD = os.environ.get("LIBRECHAT_PASSWORD") or ""
NAME = os.environ.get("LIBRECHAT_USER_NAME", "Syncer")
USERNAME = (os.environ.get("LIBRECHAT_USER_USERNAME", "syncer") or "").strip().lower()

if not EMAIL or not PASSWORD:
    sys.exit("[bootstrap] LIBRECHAT_EMAIL and LIBRECHAT_PASSWORD must be set")
if len(PASSWORD) < 8:
    sys.exit("[bootstrap] LIBRECHAT_PASSWORD must be at least 8 characters")

client = None
for _ in range(30):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        break
    except Exception:
        time.sleep(2)
else:
    sys.exit(f"[bootstrap] could not reach mongo at {MONGO_URI}")

db = client.get_default_database()
users = db["users"]

if users.find_one({"$or": [{"email": EMAIL}, {"username": USERNAME}]}):
    print(f"[bootstrap] user {EMAIL} already exists, skipping")
    sys.exit(0)

now = datetime.now(timezone.utc)
hashed = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(10)).decode()

users.insert_one({
    "email": EMAIL,
    "username": USERNAME,
    "name": NAME,
    "password": hashed,
    "provider": "local",
    "role": "USER",
    "emailVerified": True,
    "plugins": [],
    "twoFactorEnabled": False,
    "refreshToken": [],
    "createdAt": now,
    "updatedAt": now,
})

print(f"[bootstrap] created user {EMAIL}")

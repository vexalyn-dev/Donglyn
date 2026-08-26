-- ============================================================
-- VEXORA — Supabase Setup SQL
-- Jalankan di Supabase SQL Editor: https://supabase.com/dashboard
-- ============================================================

-- 1. Tabel Users (utama)
CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT,
    avatar TEXT,
    google_id TEXT,
    phone TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Auto-migrate: tambah kolom jika belum ada (aman dijalankan berulang)
DO $$ BEGIN
    ALTER TABLE users ADD COLUMN phone TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE users ADD COLUMN google_id TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

-- 2. Tabel Bookmarks
CREATE TABLE IF NOT EXISTS bookmarks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    thumbnail TEXT,
    episode TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index untuk query cepat
CREATE INDEX IF NOT EXISTS idx_bookmarks_user ON bookmarks(user_id);

-- 3. Tabel History (riwayat nonton)
CREATE TABLE IF NOT EXISTS history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    thumbnail TEXT,
    episode TEXT,
    progress TEXT,
    watched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id);

-- 4. Tabel Cache (cache scraping)
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Tabel Dev Logs (log aktivitas developer)
CREATE TABLE IF NOT EXISTS dev_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level TEXT NOT NULL DEFAULT 'INFO',
    category TEXT NOT NULL DEFAULT 'system',
    message TEXT NOT NULL
);

-- ============================================================
-- Row Level Security (RLS) — opsional, aktifkan jika perlu
-- ============================================================
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bookmarks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE history ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- Selesai! Semua tabel siap digunakan.
-- ============================================================

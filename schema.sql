-- Database Schema for Personal Diary App
-- Run this SQL in your NeonDB console to create the tables

-- Create DiaryEntry table
CREATE TABLE IF NOT EXISTS "DiaryEntry" (
    "id" TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "title" TEXT,
    "content" TEXT NOT NULL,
    "imageUrl" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on userId for faster queries
CREATE INDEX IF NOT EXISTS "DiaryEntry_userId_idx" ON "DiaryEntry"("userId");

-- Create index on createdAt for sorting
CREATE INDEX IF NOT EXISTS "DiaryEntry_createdAt_idx" ON "DiaryEntry"("createdAt" DESC);

-- Optional: Create a trigger to auto-update updatedAt
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_diary_entry_updated_at BEFORE UPDATE
    ON "DiaryEntry" FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


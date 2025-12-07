-- Supabase Database Schema for Orange Pi Dashboard
-- Run this in your Supabase SQL Editor

-- Table: reminders
CREATE TABLE IF NOT EXISTS reminders (
  id BIGSERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  priority INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reminders_active_priority 
ON reminders(active, priority DESC);

ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON reminders
FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write access" ON reminders
FOR ALL USING (auth.role() = 'authenticated');

INSERT INTO reminders (text, active, priority) VALUES
  ('Take medication at 3pm', true, 1),
  ('Team meeting at 2:30pm', true, 2),
  ('Exercise for 30 minutes', true, 3)
ON CONFLICT DO NOTHING;

-- Table: motivational_messages
CREATE TABLE IF NOT EXISTS motivational_messages (
  id BIGSERIAL PRIMARY KEY,
  text TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_motivational_active_order 
ON motivational_messages(active, display_order ASC);

ALTER TABLE motivational_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON motivational_messages
FOR SELECT USING (true);

CREATE POLICY "Allow authenticated write access" ON motivational_messages
FOR ALL USING (auth.role() = 'authenticated');

INSERT INTO motivational_messages (text, active, display_order) VALUES
  ('Focus on progress, not perfection', true, 1),
  ('Small consistent steps lead to remarkable results', true, 2),
  ('Today is an opportunity to grow', true, 3),
  ('Your health is your wealth', true, 4),
  ('Every positive choice compounds over time', true, 5)
ON CONFLICT DO NOTHING;

-- Helper function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_reminders_updated_at 
BEFORE UPDATE ON reminders
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_motivational_messages_updated_at 
BEFORE UPDATE ON motivational_messages
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


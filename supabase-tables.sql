-- =====================================================
-- Dashboard Tables for Supabase
-- Run this in your Supabase SQL Editor
-- =====================================================

-- Create reminders table
CREATE TABLE IF NOT EXISTS public.reminders (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create motivational_messages table  
CREATE TABLE IF NOT EXISTS public.motivational_messages (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.motivational_messages ENABLE ROW LEVEL SECURITY;

-- Allow public read access (for anon key)
DROP POLICY IF EXISTS "Allow public read reminders" ON public.reminders;
CREATE POLICY "Allow public read reminders" ON public.reminders 
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow public read motivational" ON public.motivational_messages;
CREATE POLICY "Allow public read motivational" ON public.motivational_messages 
    FOR SELECT USING (true);

-- Insert sample reminders
INSERT INTO public.reminders (text, priority, active) VALUES 
    ('Take your vitamins 💊', 3, true),
    ('Drink water 💧', 2, true),
    ('Stand up and stretch 🧘', 1, true),
    ('Check blood sugar 🩸', 4, true),
    ('Take a deep breath 🌬️', 0, true);

-- Insert sample motivational messages
INSERT INTO public.motivational_messages (text, display_order, active) VALUES 
    ('You are capable of amazing things ✨', 1, true),
    ('Progress over perfection 🎯', 2, true),
    ('Every day is a fresh start 🌅', 3, true),
    ('Small steps lead to big changes 👣', 4, true),
    ('You''ve got this! 💪', 5, true),
    ('Be kind to yourself today 💝', 6, true);

-- Verify tables were created
SELECT 'reminders' as table_name, count(*) as rows FROM public.reminders
UNION ALL
SELECT 'motivational_messages', count(*) FROM public.motivational_messages;

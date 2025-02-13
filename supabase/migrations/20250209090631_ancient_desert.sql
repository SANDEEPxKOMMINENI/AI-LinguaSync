/*
  # Create translations table and related schemas

  1. New Tables
    - `translations`
      - `id` (uuid, primary key)
      - `user_id` (uuid, references auth.users)
      - `original_text` (text)
      - `translated_text` (text)
      - `source_lang` (text)
      - `target_lang` (text)
      - `speaker_id` (text)
      - `audio_url` (text)
      - `created_at` (timestamptz)

  2. Security
    - Enable RLS on translations table
    - Add policies for authenticated users to:
      - Read their own translations
      - Create new translations
*/

CREATE TABLE IF NOT EXISTS translations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users NOT NULL,
  original_text text NOT NULL,
  translated_text text NOT NULL,
  source_lang text NOT NULL,
  target_lang text NOT NULL,
  speaker_id text,
  audio_url text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE translations ENABLE ROW LEVEL SECURITY;

-- Policy to allow users to read their own translations
CREATE POLICY "Users can read own translations"
  ON translations
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

-- Policy to allow users to create translations
CREATE POLICY "Users can create translations"
  ON translations
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);
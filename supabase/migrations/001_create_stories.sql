-- Enable PostGIS extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create stories table
CREATE TABLE stories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location GEOGRAPHY(POINT, 4326) NOT NULL,
  text TEXT NOT NULL,
  language VARCHAR(10) DEFAULT 'nl',
  status VARCHAR(20) DEFAULT 'approved',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_stories_location ON stories USING GIST(location);
CREATE INDEX idx_stories_status ON stories(status);
CREATE INDEX idx_stories_created_at ON stories(created_at DESC);

-- Enable Row Level Security
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can insert stories (for anonymous submissions)
CREATE POLICY "Anyone can insert stories" 
  ON stories FOR INSERT 
  WITH CHECK (true);

-- Policy: Public can only read approved stories
CREATE POLICY "Public can read approved stories"
  ON stories FOR SELECT
  USING (status = 'approved');

-- Policy: Service role can do everything (for admin operations)
CREATE POLICY "Service role has full access"
  ON stories
  USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_stories_updated_at 
  BEFORE UPDATE ON stories 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();


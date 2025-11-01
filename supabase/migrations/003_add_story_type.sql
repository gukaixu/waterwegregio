-- Add type column to stories table
ALTER TABLE stories ADD COLUMN IF NOT EXISTS type VARCHAR(50) DEFAULT 'bewoner';

-- Update the view to include the type
CREATE OR REPLACE VIEW stories_with_coords AS
SELECT 
    id,
    text,
    type,
    language,
    status,
    created_at,
    updated_at,
    ST_Y(location::geometry) as lat,
    ST_X(location::geometry) as lng
FROM stories;


-- Add optional fields to stories table
ALTER TABLE stories ADD COLUMN IF NOT EXISTS organisatie TEXT;
ALTER TABLE stories ADD COLUMN IF NOT EXISTS naam TEXT;
ALTER TABLE stories ADD COLUMN IF NOT EXISTS link TEXT;

-- Update the view to include the new fields
DROP VIEW IF EXISTS stories_with_coords;
CREATE VIEW stories_with_coords AS
SELECT
    id,
    text,
    type,
    organisatie,
    naam,
    link,
    language,
    status,
    created_at,
    updated_at,
    ST_Y(location::geometry) as lat,
    ST_X(location::geometry) as lng
FROM stories;


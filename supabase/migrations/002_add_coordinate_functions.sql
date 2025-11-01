-- Function to get story coordinates as lat/lng
CREATE OR REPLACE FUNCTION get_story_coordinates(story_id UUID)
RETURNS TABLE (lat DOUBLE PRECISION, lng DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ST_Y(location::geometry) as lat,
        ST_X(location::geometry) as lng
    FROM stories
    WHERE id = story_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- Create a view that includes lat/lng for easier querying
CREATE OR REPLACE VIEW stories_with_coords AS
SELECT 
    id,
    text,
    language,
    status,
    created_at,
    updated_at,
    ST_Y(location::geometry) as lat,
    ST_X(location::geometry) as lng
FROM stories;


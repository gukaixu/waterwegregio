// Data management utilities

// Load pins from JSON file
async function loadPins() {
    try {
        const response = await fetch('data/pins.json');
        if (!response.ok) {
            throw new Error('Failed to load pins data');
        }
        const data = await response.json();
        return data.pins || [];
    } catch (error) {
        console.error('Error loading pins:', error);
        // Return empty array if file doesn't exist or has errors
        return [];
    }
}

// Save pins to localStorage (since we can't write files from browser)
function savePins(pins) {
    try {
        const data = { pins: pins };
        localStorage.setItem('waterwegregio_pins', JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Error saving pins:', error);
        return false;
    }
}

// Get pins from localStorage (overrides JSON file if exists)
function getPinsFromStorage() {
    try {
        const stored = localStorage.getItem('waterwegregio_pins');
        if (stored) {
            const data = JSON.parse(stored);
            return data.pins || [];
        }
        return null;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return null;
    }
}

// Get all pins (from storage first, then JSON file)
async function getAllPins() {
    const storedPins = getPinsFromStorage();
    if (storedPins !== null) {
        return storedPins;
    }
    return await loadPins();
}

// Generate unique ID
function generateId() {
    return 'pin_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('nl-NL', options);
}

// Convert YouTube URL to embed URL
function getYouTubeEmbedUrl(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    if (match && match[2].length === 11) {
        return `https://www.youtube.com/embed/${match[2]}`;
    }
    return null;
}

// Convert Vimeo URL to embed URL
function getVimeoEmbedUrl(url) {
    const regExp = /vimeo.com\/(\d+)/;
    const match = url.match(regExp);
    if (match) {
        return `https://player.vimeo.com/video/${match[1]}`;
    }
    return null;
}

// Get embed URL for video (supports YouTube and Vimeo)
function getVideoEmbedUrl(url) {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
        return getYouTubeEmbedUrl(url);
    } else if (url.includes('vimeo.com')) {
        return getVimeoEmbedUrl(url);
    }
    return null;
}

// Export data to JSON file (download)
function exportToJson(pins) {
    const data = { pins: pins };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pins.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}


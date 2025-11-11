// Main map viewer functionality

let map;
let markers = [];
let boundaryLayer;

// Initialize the map
function initMap() {
    // Create map centered on Waterwegregio area
    map = L.map('map', {
        zoomControl: true,
        scrollWheelZoom: true
    }).setView([51.90, 4.40], 11);

    // Add clean CartoDB Positron tile layer for minimal look
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        maxZoom: 19
    }).addTo(map);

    // Load Waterwegregio boundary
    loadBoundary();

    // Load and display pins
    loadAndDisplayPins();
}

// Load Waterwegregio boundary
async function loadBoundary() {
    try {
        const response = await fetch('data/waterwegregio_boundary.geojson');
        if (response.ok) {
            const geojson = await response.json();
            
            // Add boundary to map with clean styling
            boundaryLayer = L.geoJSON(geojson, {
                style: {
                    color: '#0066cc',
                    weight: 3,
                    opacity: 0.8,
                    fillColor: '#0066cc',
                    fillOpacity: 0.05,
                    dashArray: '8, 4'
                }
            }).addTo(map);
            
            // Fit map to boundary
            map.fitBounds(boundaryLayer.getBounds(), { padding: [30, 30] });
        }
    } catch (error) {
        console.error('Error loading boundary:', error);
    }
}

// Load pins and display on map
async function loadAndDisplayPins() {
    try {
        const pins = await getAllPins();
        
        // Clear existing markers
        markers.forEach(marker => marker.remove());
        markers = [];

        // Add marker for each pin
        pins.forEach(pin => {
            addMarkerToMap(pin);
        });

        // Fit bounds if we have pins and no boundary layer
        if (pins.length > 0 && !boundaryLayer) {
            const bounds = L.latLngBounds(pins.map(pin => [pin.lat, pin.lng]));
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    } catch (error) {
        console.error('Error loading pins:', error);
    }
}

// Get icon for pin type
function getIconForType(type) {
    const icons = {
        'story': '📖',
        'photo': '📷',
        'video': '🎥',
        'event': '🎉',
        'place': '🏛️',
        'nature': '🌳'
    };
    return icons[type] || '📌';
}

// Add a marker to the map
function addMarkerToMap(pin) {
    const pinType = pin.type || 'story';
    const iconEmoji = getIconForType(pinType);
    
    // Create custom icon
    const icon = L.divIcon({
        className: `custom-marker marker-${pinType}`,
        html: iconEmoji,
        iconSize: [50, 50],
        iconAnchor: [25, 50],
        popupAnchor: [0, -50]
    });

    // Create marker
    const marker = L.marker([pin.lat, pin.lng], { icon: icon });

    // Create popup content
    const popupContent = createPopupContent(pin);

    // Bind popup
    marker.bindPopup(popupContent, {
        maxWidth: 400,
        className: 'custom-popup'
    });

    // Add to map
    marker.addTo(map);
    markers.push(marker);
}

// Create popup content HTML
function createPopupContent(pin) {
    let html = '<div class="popup-content">';
    
    // Header
    html += '<div class="popup-header">';
    html += `<h3>${escapeHtml(pin.title)}</h3>`;
    if (pin.location) {
        html += `<div class="popup-location">${escapeHtml(pin.location)}</div>`;
    }
    html += '</div>';

    // Description
    if (pin.description) {
        html += `<div class="popup-description">${escapeHtml(pin.description)}</div>`;
    }

    // Images
    if (pin.images && pin.images.length > 0) {
        html += '<div class="popup-images">';
        html += '<div class="image-gallery">';
        pin.images.forEach(imageUrl => {
            if (imageUrl.trim()) {
                html += `<img src="${escapeHtml(imageUrl)}" alt="Foto" onclick="window.open('${escapeHtml(imageUrl)}', '_blank')">`;
            }
        });
        html += '</div>';
        html += '</div>';
    }

    // Videos
    if (pin.videos && pin.videos.length > 0) {
        html += '<div class="popup-videos">';
        html += '<h4>Video\'s</h4>';
        pin.videos.forEach(videoUrl => {
            if (videoUrl.trim()) {
                const embedUrl = getVideoEmbedUrl(videoUrl);
                if (embedUrl) {
                    html += '<div class="video-container">';
                    html += `<iframe src="${embedUrl}" allowfullscreen></iframe>`;
                    html += '</div>';
                }
            }
        });
        html += '</div>';
    }

    // Date
    if (pin.created) {
        html += `<div class="popup-date">Toegevoegd: ${formatDate(pin.created)}</div>`;
    }

    html += '</div>';
    return html;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', initMap);


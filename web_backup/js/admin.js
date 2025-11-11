// Admin interface functionality

const ADMIN_PASSWORD = 'waterweg2025'; // Simple password for prototype
let adminMap;
let selectedMarker;
let selectedLat, selectedLng;
let currentEditingId = null;
let allPins = [];

// Login function
function login() {
    const password = document.getElementById('password-input').value;
    const errorMsg = document.getElementById('error-message');
    
    if (password === ADMIN_PASSWORD) {
        // Store login state
        sessionStorage.setItem('admin_logged_in', 'true');
        
        // Hide login screen and show admin interface
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('admin-interface').style.display = 'block';
        
        // Initialize admin interface
        initAdminInterface();
    } else {
        errorMsg.textContent = 'Onjuist wachtwoord';
    }
}

// Check if already logged in
function checkLoginStatus() {
    if (sessionStorage.getItem('admin_logged_in') === 'true') {
        document.getElementById('login-screen').style.display = 'none';
        document.getElementById('admin-interface').style.display = 'block';
        initAdminInterface();
    }
}

// Initialize admin interface
async function initAdminInterface() {
    // Initialize map
    initAdminMap();
    
    // Load pins
    await loadPinsList();
    
    // Set up form handler
    document.getElementById('pin-form').addEventListener('submit', handleFormSubmit);
}

// Initialize admin map
function initAdminMap() {
    adminMap = L.map('admin-map').setView([51.90, 4.40], 11);
    
    // Use clean CartoDB tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 19
    }).addTo(adminMap);
    
    // Load and show boundary
    loadAdminBoundary();
    
    // Add click handler
    adminMap.on('click', handleMapClick);
}

// Load boundary on admin map
async function loadAdminBoundary() {
    try {
        const response = await fetch('data/waterwegregio_boundary.geojson');
        if (response.ok) {
            const geojson = await response.json();
            
            L.geoJSON(geojson, {
                style: {
                    color: '#0066cc',
                    weight: 3,
                    opacity: 0.8,
                    fillColor: '#0066cc',
                    fillOpacity: 0.05,
                    dashArray: '8, 4'
                }
            }).addTo(adminMap);
        }
    } catch (error) {
        console.error('Error loading boundary:', error);
    }
}

// Handle map click
function handleMapClick(e) {
    selectedLat = e.latlng.lat;
    selectedLng = e.latlng.lng;
    
    // Remove previous marker
    if (selectedMarker) {
        selectedMarker.remove();
    }
    
    // Get selected pin type
    const pinType = document.getElementById('pin-type')?.value || 'story';
    const icons = {
        'story': '📖',
        'photo': '📷',
        'video': '🎥',
        'event': '🎉',
        'place': '🏛️',
        'nature': '🌳'
    };
    
    // Add new marker
    const icon = L.divIcon({
        className: `custom-marker marker-${pinType}`,
        html: icons[pinType] || '📍',
        iconSize: [50, 50],
        iconAnchor: [25, 50]
    });
    
    selectedMarker = L.marker([selectedLat, selectedLng], { icon: icon }).addTo(adminMap);
    
    // Update coordinates display
    const coordsEl = document.getElementById('selected-coords');
    coordsEl.textContent = `Geselecteerd: ${selectedLat.toFixed(6)}, ${selectedLng.toFixed(6)}`;
    coordsEl.classList.add('active');
    
    // Update hidden form fields
    document.getElementById('pin-lat').value = selectedLat;
    document.getElementById('pin-lng').value = selectedLng;
}

// Load and display pins list
async function loadPinsList() {
    allPins = await getAllPins();
    displayPinsList();
}

// Display pins list
function displayPinsList() {
    const listEl = document.getElementById('pins-list');
    const countEl = document.getElementById('pins-count');
    
    countEl.textContent = allPins.length;
    
    if (allPins.length === 0) {
        listEl.innerHTML = '<div class="no-pins">Nog geen verhalen toegevoegd</div>';
        return;
    }
    
    listEl.innerHTML = '';
    
    allPins.forEach(pin => {
        const item = createPinListItem(pin);
        listEl.appendChild(item);
    });
}

// Create pin list item
function createPinListItem(pin) {
    const div = document.createElement('div');
    div.className = 'pin-item';
    
    const content = document.createElement('div');
    content.className = 'pin-item-content';
    
    const title = document.createElement('h3');
    title.textContent = pin.title;
    content.appendChild(title);
    
    const meta = document.createElement('div');
    meta.className = 'pin-item-meta';
    meta.textContent = `${pin.location || 'Geen locatie'} • ${formatDate(pin.created)}`;
    content.appendChild(meta);
    
    if (pin.description) {
        const desc = document.createElement('div');
        desc.className = 'pin-item-description';
        desc.textContent = pin.description.substring(0, 150) + (pin.description.length > 150 ? '...' : '');
        content.appendChild(desc);
    }
    
    div.appendChild(content);
    
    const actions = document.createElement('div');
    actions.className = 'pin-item-actions';
    
    const editBtn = document.createElement('button');
    editBtn.className = 'btn-edit';
    editBtn.textContent = 'Bewerken';
    editBtn.onclick = () => editPin(pin);
    actions.appendChild(editBtn);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-delete';
    deleteBtn.textContent = 'Verwijderen';
    deleteBtn.onclick = () => deletePin(pin.id);
    actions.appendChild(deleteBtn);
    
    div.appendChild(actions);
    
    return div;
}

// Handle form submit
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Validate location is selected
    const lat = document.getElementById('pin-lat').value;
    const lng = document.getElementById('pin-lng').value;
    
    if (!lat || !lng) {
        alert('Selecteer eerst een locatie op de kaart');
        return;
    }
    
    // Get form data
    const pinData = {
        id: currentEditingId || generateId(),
        type: document.getElementById('pin-type').value,
        lat: parseFloat(lat),
        lng: parseFloat(lng),
        title: document.getElementById('pin-title').value,
        location: document.getElementById('pin-location').value,
        description: document.getElementById('pin-description').value,
        images: document.getElementById('pin-images').value.split('\n').filter(url => url.trim()),
        videos: document.getElementById('pin-videos').value.split('\n').filter(url => url.trim()),
        created: currentEditingId ? findPinById(currentEditingId).created : new Date().toISOString()
    };
    
    // Save pin
    if (currentEditingId) {
        // Update existing pin
        const index = allPins.findIndex(p => p.id === currentEditingId);
        if (index !== -1) {
            allPins[index] = pinData;
        }
    } else {
        // Add new pin
        allPins.push(pinData);
    }
    
    // Save to storage
    savePins(allPins);
    
    // Reset form
    resetForm();
    
    // Reload list
    displayPinsList();
    
    // Show success message
    alert(currentEditingId ? 'Verhaal bijgewerkt!' : 'Verhaal toegevoegd!');
}

// Edit pin
function editPin(pin) {
    currentEditingId = pin.id;
    
    // Update form title
    document.getElementById('form-title').textContent = 'Verhaal Bewerken';
    
    // Fill form
    document.getElementById('pin-id').value = pin.id;
    document.getElementById('pin-type').value = pin.type || 'story';
    document.getElementById('pin-lat').value = pin.lat;
    document.getElementById('pin-lng').value = pin.lng;
    document.getElementById('pin-title').value = pin.title;
    document.getElementById('pin-location').value = pin.location || '';
    document.getElementById('pin-description').value = pin.description;
    document.getElementById('pin-images').value = pin.images.join('\n');
    document.getElementById('pin-videos').value = pin.videos.join('\n');
    
    // Update map
    selectedLat = pin.lat;
    selectedLng = pin.lng;
    
    if (selectedMarker) {
        selectedMarker.remove();
    }
    
    const pinType = pin.type || 'story';
    const icons = {
        'story': '📖',
        'photo': '📷',
        'video': '🎥',
        'event': '🎉',
        'place': '🏛️',
        'nature': '🌳'
    };
    
    const icon = L.divIcon({
        className: `custom-marker marker-${pinType}`,
        html: icons[pinType] || '📍',
        iconSize: [50, 50],
        iconAnchor: [25, 50]
    });
    
    selectedMarker = L.marker([selectedLat, selectedLng], { icon: icon }).addTo(adminMap);
    adminMap.setView([selectedLat, selectedLng], 14);
    
    // Update coordinates display
    const coordsEl = document.getElementById('selected-coords');
    coordsEl.textContent = `Geselecteerd: ${selectedLat.toFixed(6)}, ${selectedLng.toFixed(6)}`;
    coordsEl.classList.add('active');
    
    // Scroll to form
    document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
}

// Delete pin
function deletePin(id) {
    if (confirm('Weet je zeker dat je dit verhaal wilt verwijderen?')) {
        allPins = allPins.filter(p => p.id !== id);
        savePins(allPins);
        displayPinsList();
    }
}

// Reset form
function resetForm() {
    currentEditingId = null;
    document.getElementById('form-title').textContent = 'Nieuw Verhaal Toevoegen';
    document.getElementById('pin-form').reset();
    document.getElementById('pin-id').value = '';
    document.getElementById('pin-lat').value = '';
    document.getElementById('pin-lng').value = '';
    
    if (selectedMarker) {
        selectedMarker.remove();
        selectedMarker = null;
    }
    
    const coordsEl = document.getElementById('selected-coords');
    coordsEl.textContent = 'Geen locatie geselecteerd';
    coordsEl.classList.remove('active');
}

// Find pin by ID
function findPinById(id) {
    return allPins.find(p => p.id === id);
}

// Export data
function exportData() {
    exportToJson(allPins);
    alert('Data geëxporteerd naar pins.json. Upload dit bestand naar de data/ folder om wijzigingen permanent te maken.');
}

// Allow Enter key in password field
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('password-input');
    if (passwordInput) {
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                login();
            }
        });
    }
    
    // Check login status
    checkLoginStatus();
});


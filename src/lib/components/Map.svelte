<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import maplibregl from 'maplibre-gl';
	import { supabase, storyTypes } from '$lib/supabase';
	import type { StoryWithCoords } from '$lib/supabase';

	const dispatch = createEventDispatcher();

	let mapContainer: HTMLDivElement;
	let map: maplibregl.Map;

	export let stories: StoryWithCoords[] = [];

	let boundaryGeojson: any = null;
	let tempMarker: maplibregl.Marker | null = null;
	let storiesLayerAdded = false;
	let storyMarkers: maplibregl.Marker[] = [];
	let currentPopup: maplibregl.Popup | null = null;
	let markersRendered = false;

	// Only render markers once when both map and stories are ready
	$: if (map && storiesLayerAdded && stories.length > 0 && !markersRendered) {
		renderStoryMarkers();
		markersRendered = true;
	}

	onMount(async () => {
		// Load custom Maputnik style
		const styleResponse = await fetch('/map-style-2.json');
		const customStyle = await styleResponse.json();

		// Initialize map with custom style
		map = new maplibregl.Map({
			container: mapContainer,
			style: customStyle,
			center: [4.4, 51.9],
			zoom: 11
		});

		// Add navigation controls
		map.addControl(new maplibregl.NavigationControl(), 'top-right');

		// Custom cursor for pin placement - using a pin emoji as cursor
		const cursorSize = 32;
		const pinCursor = `data:image/svg+xml,${encodeURIComponent(`
			<svg width="${cursorSize}" height="${cursorSize}" xmlns="http://www.w3.org/2000/svg">
				<text x="${cursorSize/2}" y="${cursorSize/2}" font-size="24" text-anchor="middle" dominant-baseline="central">📍</text>
			</svg>
		`)}`;
		map.getCanvas().style.cursor = `url('${pinCursor}') ${cursorSize/2} ${cursorSize}, auto`;

		// Track mouse movement to update cursor based on boundary
		map.on('mousemove', (e) => {
			// Check if hovering over a story marker first
			const hoveredElements = document.elementsFromPoint(e.originalEvent.clientX, e.originalEvent.clientY);
			const isHoveringMarker = hoveredElements.some(el => 
				el.classList.contains('story-marker-wrapper') || el.classList.contains('story-marker-icon')
			);
			
			if (isHoveringMarker) {
				// Let the marker's cursor style take precedence
				return;
			}
			
			if (boundaryGeojson && isPointInBoundary(e.lngLat.lng, e.lngLat.lat)) {
				map.getCanvas().style.cursor = `url('${pinCursor}') ${cursorSize/2} ${cursorSize}, auto`;
			} else if (boundaryGeojson) {
				map.getCanvas().style.cursor = 'not-allowed';
			}
		});

		// Wait for map to load
		map.on('load', () => {
			// Load and add boundary
			loadBoundary();
			
			// Load municipality boundaries
			loadMunicipalityBoundaries();

			// Add stories layer (even if empty, will be populated when stories load)
			addStoriesLayer();
			storiesLayerAdded = true;

			// Handle map clicks for new story placement
			map.on('click', (e) => {

				const clickLng = e.lngLat.lng;
				const clickLat = e.lngLat.lat;
				console.log(`Clicked at: ${clickLat.toFixed(4)}, ${clickLng.toFixed(4)}`);
				
				// Check if click is inside boundary
				if (isPointInBoundary(clickLng, clickLat)) {
					console.log('✓ Inside boundary - showing confirmation');
					showLocationConfirmation(clickLng, clickLat);
				} else {
					console.log('✗ Outside boundary - showing warning');
					dispatch('outsideboundary');
				}
			});

		});

		return () => {
			map?.remove();
		};
	});

	async function loadBoundary() {
		try {
			const response = await fetch('/data/waterwegregio_boundary.geojson');
			const geojson = await response.json();
			boundaryGeojson = geojson; // Store for point-in-polygon checks

			// Add boundary source
			map.addSource('boundary', {
				type: 'geojson',
				data: geojson
			});

			// Add boundary fill (subtle highlight)
			map.addLayer({
				id: 'boundary-fill',
				type: 'fill',
				source: 'boundary',
				paint: {
					'fill-color': '#1e5a8e',
					'fill-opacity': 0.1
				}
			});

		// Add boundary line (prominent yellow border)
		map.addLayer({
			id: 'boundary-line',
			type: 'line',
			source: 'boundary',
			paint: {
				'line-color': '#ffd900',
				'line-width': 6,
				'line-opacity': 1
			}
		});
		
		// Add boundary line shadow for more prominence
		map.addLayer({
			id: 'boundary-line-shadow',
			type: 'line',
			source: 'boundary',
			paint: {
				'line-color': '#ffffff',
				'line-width': 8,
				'line-opacity': 0.6,
				'line-blur': 2
			}
		}, 'boundary-line');
			
			// Create inverse mask - polygon with hole for waterwegregio
			// This will darken everything OUTSIDE the boundary
			const inverseMask = createInverseMask(geojson);
			
			map.addSource('inverse-mask', {
				type: 'geojson',
				data: inverseMask
			});
			
			map.addLayer({
				id: 'outside-overlay',
				type: 'fill',
				source: 'inverse-mask',
				paint: {
					'fill-color': '#e8e8e8',
					'fill-opacity': 0.7
				}
			});

			// Fit map to boundary
			const bounds = new maplibregl.LngLatBounds();
			geojson.features.forEach((feature: any) => {
				if (feature.geometry.type === 'Polygon') {
					feature.geometry.coordinates[0].forEach((coord: [number, number]) => {
						bounds.extend(coord);
					});
				} else if (feature.geometry.type === 'MultiPolygon') {
					feature.geometry.coordinates.forEach((polygon: any) => {
						polygon[0].forEach((coord: [number, number]) => {
							bounds.extend(coord);
						});
					});
				}
			});
			map.fitBounds(bounds, { padding: 30 });
		} catch (error) {
			console.error('Error loading boundary:', error);
		}
	}

	async function loadMunicipalityBoundaries() {
		try {
			const response = await fetch('/data/municipality_boundaries.geojson');
			const geojson = await response.json();

		// Filter out Rotterdam (GM0599) - we don't need to show its boundary
		const filteredGeojson = {
			type: 'FeatureCollection',
			features: geojson.features.filter((feature: any) => 
				feature.properties && feature.properties.code !== 'GM0599'
			)
		};

			// Add municipality boundaries source
			map.addSource('municipality-boundaries', {
				type: 'geojson',
				data: filteredGeojson
			});

		// Add municipality boundaries as subtle dotted yellow lines
		map.addLayer({
			id: 'municipality-boundaries',
			type: 'line',
			source: 'municipality-boundaries',
			paint: {
				'line-color': '#ffd900',
				'line-width': 2,
				'line-dasharray': [1, 1]
			}
		}, 'boundary-line'); // Place below the main boundary line

			console.log('Municipality boundaries loaded (excluding Rotterdam)');
		} catch (error) {
			console.error('Error loading municipality boundaries:', error);
		}
	}

	function addStoriesLayer() {
		console.log(`🗺️ Initial stories layer setup (${stories.length} stories)`);
		// We'll use HTML markers instead of symbol layers for reliable emoji rendering
	}

	function renderStoryMarkers() {
		console.log(`🔄 Rendering ${stories.length} story markers`);
		
		// Remove existing markers
		storyMarkers.forEach(marker => marker.remove());
		storyMarkers = [];

		// Create new markers for each story
		stories.forEach((story) => {
			const typeConfig = storyTypes[story.type] || storyTypes.bewoner;
			
			// Create marker element wrapper
			const el = document.createElement('div');
			el.className = 'story-marker-wrapper';
			
			// Create img element for the icon
			const icon = document.createElement('img');
			icon.className = story.type === 'project' ? 'story-marker-icon project-icon' : 'story-marker-icon';
			icon.src = typeConfig.icon;
			icon.alt = typeConfig.label;
			
			el.appendChild(icon);
			
			// Add gradient overlay for project icons
			if (story.type === 'project') {
				const gradientOverlay = document.createElement('div');
				gradientOverlay.className = 'project-gradient-overlay';
				el.appendChild(gradientOverlay);
			}

			// Create marker with anchor at center
			const marker = new maplibregl.Marker({ 
				element: el,
				anchor: 'center'
			})
				.setLngLat([story.lng, story.lat])
				.addTo(map);

			// Add click handler for popup
			el.addEventListener('click', (e) => {
				e.stopPropagation();
				const created = story.created_at
					? new Date(story.created_at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'long', year: 'numeric' })
					: '';

				let popupHTML = `
					<div class="popup-content">
						<div class="popup-header">
							<div class="popup-icon-container ${story.type === 'project' ? 'popup-icon-project' : ''}">
								<img src="${typeConfig.icon}" alt="${escapeHtml(typeConfig.label)}" class="popup-icon-img" />
							</div>
							<span class="popup-type">${escapeHtml(typeConfig.label)}</span>
						</div>
						<p class="popup-text">${escapeHtml(story.text)}</p>
				`;

				// Add optional fields in a cleaner format
				const metaFields = [];
				if (story.organisatie) {
					metaFields.push(`<div class="popup-meta-item"><span class="popup-meta-label">Organisatie</span><span class="popup-meta-value">${escapeHtml(story.organisatie)}</span></div>`);
				}
				if (story.naam) {
					metaFields.push(`<div class="popup-meta-item"><span class="popup-meta-label">Naam</span><span class="popup-meta-value">${escapeHtml(story.naam)}</span></div>`);
				}
				if (story.link) {
					const fullUrl = story.link.startsWith('http://') || story.link.startsWith('https://') 
						? story.link 
						: 'https://' + story.link;
					metaFields.push(`<div class="popup-meta-item"><span class="popup-meta-label">Link</span><a href="${escapeHtml(fullUrl)}" target="_blank" rel="noopener noreferrer" class="popup-meta-link">${escapeHtml(story.link)}</a></div>`);
				}

				if (metaFields.length > 0) {
					popupHTML += `<div class="popup-meta-section">${metaFields.join('')}</div>`;
				}

				if (created) {
					popupHTML += `<div class="popup-date">📅 ${created}</div>`;
				}

				popupHTML += `</div>`;

				// Close any existing popup before opening a new one
				if (currentPopup) {
					currentPopup.remove();
				}

				// Create and store the new popup
				currentPopup = new maplibregl.Popup({ offset: 25, className: `popup-${story.type}` })
					.setLngLat([story.lng, story.lat])
					.setHTML(popupHTML)
					.addTo(map);
				
				// Clear the reference when popup is closed
				currentPopup.on('close', () => {
					currentPopup = null;
				});
			});

			storyMarkers.push(marker);
		});

		console.log(`✅ Rendered ${storyMarkers.length} markers on map`);
	}

	export function refreshStories(newStories: StoryWithCoords[]) {
		stories = newStories;
		markersRendered = false; // Allow re-render with new stories
	}

	function escapeHtml(text: string): string {
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}

	// Create inverse mask - a world polygon with holes for the boundary
	function createInverseMask(geojson: any) {
		const holes: any[] = [];
		
		geojson.features.forEach((feature: any) => {
			if (feature.geometry.type === 'Polygon') {
				holes.push(feature.geometry.coordinates[0]);
			} else if (feature.geometry.type === 'MultiPolygon') {
				feature.geometry.coordinates.forEach((polygon: any) => {
					holes.push(polygon[0]);
				});
			}
		});

		return {
			type: 'Feature',
			geometry: {
				type: 'Polygon',
				coordinates: [
					// Outer ring (world bounds)
					[
						[-180, -90],
						[-180, 90],
						[180, 90],
						[180, -90],
						[-180, -90]
					],
					// Inner rings (holes for waterwegregio)
					...holes
				]
			}
		};
	}

	// Check if a point is inside the boundary using ray casting algorithm
	function isPointInBoundary(lng: number, lat: number): boolean {
		if (!boundaryGeojson) return true; // Allow if boundary not loaded yet

		for (const feature of boundaryGeojson.features) {
			if (feature.geometry.type === 'Polygon') {
				if (pointInPolygon([lng, lat], feature.geometry.coordinates[0])) {
					return true;
				}
			} else if (feature.geometry.type === 'MultiPolygon') {
				for (const polygon of feature.geometry.coordinates) {
					if (pointInPolygon([lng, lat], polygon[0])) {
						return true;
					}
				}
			}
		}
		return false;
	}

	// Ray casting algorithm for point-in-polygon test
	function pointInPolygon(point: [number, number], polygon: [number, number][]): boolean {
		const [x, y] = point;
		let inside = false;

		for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
			const [xi, yi] = polygon[i];
			const [xj, yj] = polygon[j];

			const intersect = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
			if (intersect) inside = !inside;
		}

		return inside;
	}

	// Show location confirmation with temporary marker
	function showLocationConfirmation(lng: number, lat: number) {
		// Close any existing popup
		if (currentPopup) {
			currentPopup.remove();
			currentPopup = null;
		}

		// Remove any existing temporary marker
		if (tempMarker) {
			tempMarker.remove();
		}

		// Create a temporary marker element
		const el = document.createElement('div');
		el.className = 'temp-marker';
		el.innerHTML = '📍';
		
		// Create the marker
		tempMarker = new maplibregl.Marker({ element: el })
			.setLngLat([lng, lat])
			.addTo(map);

		// Create confirmation popup and store it in currentPopup
		currentPopup = new maplibregl.Popup({ 
			closeButton: false,
			closeOnClick: false,
			offset: 25
		})
			.setLngLat([lng, lat])
			.setHTML(`
				<div class="location-confirmation">
					<p style="margin: 0 0 12px 0; font-weight: 500;">📍 Verhaal hier plaatsen?</p>
					<div style="display: flex; gap: 8px;">
						<button class="confirm-btn" id="confirm-location">Ja</button>
						<button class="cancel-btn" id="cancel-location">Annuleren</button>
					</div>
				</div>
			`)
			.addTo(map);

		// Clear the reference when popup is closed
		currentPopup.on('close', () => {
			currentPopup = null;
			if (tempMarker) {
				tempMarker.remove();
				tempMarker = null;
			}
		});

		// Handle confirmation
		setTimeout(() => {
			const confirmBtn = document.getElementById('confirm-location');
			const cancelBtn = document.getElementById('cancel-location');

			if (confirmBtn) {
				confirmBtn.onclick = () => {
					if (currentPopup) currentPopup.remove();
					if (tempMarker) tempMarker.remove();
					currentPopup = null;
					tempMarker = null;
					dispatch('mapclick', { lng, lat });
				};
			}

			if (cancelBtn) {
				cancelBtn.onclick = () => {
					if (currentPopup) currentPopup.remove();
					if (tempMarker) tempMarker.remove();
					currentPopup = null;
					tempMarker = null;
				};
			}
		}, 100);
	}
</script>

<div bind:this={mapContainer} class="map-container"></div>

<style>
	.map-container {
		width: 100%;
		height: 100%;
	}

	:global(.maplibregl-popup-content) {
		padding: 0;
		border-radius: 12px;
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
		min-width: 260px;
		max-width: 320px;
		overflow: hidden;
		border: none;
		border-left: 4px solid #1e5a8e; /* Default blue, will be overridden */
	}
	
	/* Color-coded borders for different story types */
	:global(.maplibregl-popup-content.popup-bewoner) {
		border-left-color: #1e5a8e; /* Blue */
	}
	
	:global(.maplibregl-popup-content.popup-project) {
		border-left-color: #dc2626; /* Red/Orange */
	}
	
	:global(.maplibregl-popup-content.popup-initiatief) {
		border-left-color: #059669; /* Green */
	}
	
	:global(.maplibregl-popup-content.popup-vraag) {
		border-left-color: #ea580c; /* Orange */
	}
	
	:global(.maplibregl-popup-content.popup-idee) {
		border-left-color: #7c3aed; /* Purple */
	}

	:global(.maplibregl-popup-close-button) {
		font-size: 22px;
		padding: 8px 12px;
		color: #6b7280;
		transition: color 0.2s ease;
		background: transparent;
		position: absolute;
		right: 8px;
		top: 8px;
		z-index: 10;
	}

	:global(.maplibregl-popup-close-button:hover) {
		color: #1e5a8e;
	}

	:global(.popup-content) {
		font-family: system-ui, -apple-system, sans-serif;
		padding: 20px;
	}

	:global(.popup-header) {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 14px;
		padding-bottom: 12px;
		border-bottom: 2px solid #e5e7eb;
	}

	:global(.popup-icon-container) {
		position: relative;
		width: 28px;
		height: 28px;
		flex-shrink: 0;
	}
	
	:global(.popup-icon-img) {
		width: auto;
		height: 28px;
		object-fit: contain;
		display: block;
	}
	
	/* Navy blue for Verhaal Bewoner */
	:global(.popup-icon-img[alt="Verhaal Bewoner"]) {
		filter: brightness(0) saturate(100%) invert(28%) sepia(65%) saturate(1234%) hue-rotate(186deg) brightness(93%) contrast(88%);
	}
	
	/* Green for Lokaal Initiatief */
	:global(.popup-icon-img[alt="Lokaal Initiatief"]) {
		filter: brightness(0) saturate(100%) invert(38%) sepia(71%) saturate(1234%) hue-rotate(130deg) brightness(95%) contrast(96%);
	}
	
	/* Orange for Vraag of Behoefte */
	:global(.popup-icon-img[alt="Vraag of Behoefte"]) {
		filter: brightness(0) saturate(100%) invert(42%) sepia(95%) saturate(2413%) hue-rotate(1deg) brightness(99%) contrast(93%);
	}
	
	/* Purple for Idee */
	:global(.popup-icon-img[alt="Idee"]) {
		filter: brightness(0) saturate(100%) invert(35%) sepia(93%) saturate(2718%) hue-rotate(249deg) brightness(93%) contrast(93%);
	}
	
	/* Gradient for project puzzle in popup */
	:global(.popup-icon-project) {
		background: linear-gradient(135deg, 
			#1e5a8e 0%, 
			#dc2626 25%, 
			#fbbf24 50%, 
			#059669 75%, 
			#7c3aed 100%);
		mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
		-webkit-mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
	}
	
	:global(.popup-icon-project .popup-icon-img) {
		opacity: 0;
	}

	:global(.popup-type) {
		font-weight: 700;
		font-size: 14px;
		color: #1e5a8e;
		letter-spacing: 0.3px;
	}

	:global(.popup-text) {
		margin: 0 0 12px 0;
		font-size: 15px;
		line-height: 1.7;
		color: #1f2937;
		font-weight: 400;
		font-style: italic;
		position: relative;
		padding-left: 12px;
		border-left: 3px solid #e5e7eb;
	}

	:global(.popup-meta-section) {
		background: #f9fafb;
		padding: 12px;
		border-radius: 8px;
		margin-bottom: 12px;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	:global(.popup-meta-item) {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	:global(.popup-meta-label) {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: #6b7280;
		font-weight: 600;
	}

	:global(.popup-meta-value) {
		font-size: 14px;
		color: #374151;
		font-weight: 500;
	}

	:global(.popup-meta-link) {
		color: #1e5a8e;
		text-decoration: none;
		font-size: 14px;
		font-weight: 500;
		word-break: break-word;
		transition: color 0.2s ease;
	}

	:global(.popup-meta-link:hover) {
		color: #2563eb;
		text-decoration: underline;
	}

	:global(.popup-date) {
		font-size: 12px;
		color: #9ca3af;
		text-align: center;
		padding-top: 8px;
		border-top: 1px solid #e5e7eb;
		margin-top: 4px;
	}

	:global(.temp-marker) {
		font-size: 32px;
		cursor: pointer;
		animation: bounce-marker 0.6s ease-in-out;
	}

	@keyframes bounce-marker {
		0%, 100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-10px);
		}
	}

	:global(.location-confirmation) {
		padding: 4px;
		font-family: system-ui, -apple-system, sans-serif;
	}

	:global(.confirm-btn),
	:global(.cancel-btn) {
		padding: 6px 16px;
		border: none;
		border-radius: 6px;
		font-size: 13px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	:global(.confirm-btn) {
		background: #1e5a8e;
		color: white;
	}

	:global(.confirm-btn:hover) {
		background: #164370;
	}

	:global(.cancel-btn) {
		background: #e5e7eb;
		color: #374151;
	}

	:global(.cancel-btn:hover) {
		background: #d1d5db;
	}

	:global(.story-marker-wrapper) {
		cursor: pointer;
		user-select: none;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}

	:global(.story-marker-icon) {
		display: block;
		width: auto;
		height: 56px;
		object-fit: contain;
		transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), filter 0.25s ease;
		transform-origin: center center;
	}
	
	/* Navy blue for Verhaal Bewoner */
	:global(.story-marker-icon[alt="Verhaal Bewoner"]) {
		filter: brightness(0) saturate(100%) invert(28%) sepia(65%) saturate(1234%) hue-rotate(186deg) brightness(93%) contrast(88%) drop-shadow(0 0 3px white) drop-shadow(0 0 6px white);
	}
	
	/* Green for Lokaal Initiatief */
	:global(.story-marker-icon[alt="Lokaal Initiatief"]) {
		filter: brightness(0) saturate(100%) invert(38%) sepia(71%) saturate(1234%) hue-rotate(130deg) brightness(95%) contrast(96%) drop-shadow(0 0 3px white) drop-shadow(0 0 6px white);
	}
	
	/* Orange for Vraag of Behoefte */
	:global(.story-marker-icon[alt="Vraag of Behoefte"]) {
		filter: brightness(0) saturate(100%) invert(42%) sepia(95%) saturate(2413%) hue-rotate(1deg) brightness(99%) contrast(93%) drop-shadow(0 0 3px white) drop-shadow(0 0 6px white);
	}
	
	/* Purple for Idee */
	:global(.story-marker-icon[alt="Idee"]) {
		filter: brightness(0) saturate(100%) invert(35%) sepia(93%) saturate(2718%) hue-rotate(249deg) brightness(93%) contrast(93%) drop-shadow(0 0 3px white) drop-shadow(0 0 6px white);
	}
	
	:global(.story-marker-icon.project-icon) {
		height: 110px;
		opacity: 0;
		filter: none !important;
	}
	
	/* Gradient overlay for project puzzle pieces */
	:global(.project-gradient-overlay) {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 110px;
		height: 110px;
		background: linear-gradient(135deg, 
			#1e5a8e 0%, 
			#dc2626 25%, 
			#fbbf24 50%, 
			#059669 75%, 
			#7c3aed 100%);
		mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
		-webkit-mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
		pointer-events: none;
		filter: drop-shadow(0 0 4px white) drop-shadow(0 0 6px rgba(255, 255, 255, 0.8));
		transition: filter 0.25s ease, transform 0.25s ease;
	}

	:global(.story-marker-wrapper:hover .story-marker-icon) {
		transform: scale(1.15);
	}
	
	/* Enhanced hover effects per type */
	:global(.story-marker-wrapper:hover .story-marker-icon[alt="Verhaal Bewoner"]) {
		filter: brightness(0) saturate(100%) invert(28%) sepia(65%) saturate(1234%) hue-rotate(186deg) brightness(93%) contrast(88%) drop-shadow(0 0 4px white) drop-shadow(0 0 10px rgba(30, 90, 142, 0.5));
	}
	
	:global(.story-marker-wrapper:hover .story-marker-icon[alt="Lokaal Initiatief"]) {
		filter: brightness(0) saturate(100%) invert(38%) sepia(71%) saturate(1234%) hue-rotate(130deg) brightness(95%) contrast(96%) drop-shadow(0 0 4px white) drop-shadow(0 0 10px rgba(5, 150, 105, 0.5));
	}
	
	:global(.story-marker-wrapper:hover .story-marker-icon[alt="Vraag of Behoefte"]) {
		filter: brightness(0) saturate(100%) invert(42%) sepia(95%) saturate(2413%) hue-rotate(1deg) brightness(99%) contrast(93%) drop-shadow(0 0 4px white) drop-shadow(0 0 10px rgba(234, 88, 12, 0.5));
	}
	
	:global(.story-marker-wrapper:hover .story-marker-icon[alt="Idee"]) {
		filter: brightness(0) saturate(100%) invert(35%) sepia(93%) saturate(2718%) hue-rotate(249deg) brightness(93%) contrast(93%) drop-shadow(0 0 4px white) drop-shadow(0 0 10px rgba(124, 58, 237, 0.5));
	}
	
	:global(.story-marker-wrapper:hover .project-gradient-overlay) {
		transform: translate(-50%, -50%) scale(1.15);
		filter: drop-shadow(0 0 6px white) drop-shadow(0 0 12px rgba(255, 193, 7, 0.6)) drop-shadow(0 0 16px rgba(30, 90, 142, 0.4));
	}
</style>


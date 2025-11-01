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

	// Reactive statement to update stories when they change
	$: if (map && stories.length > 0 && storiesLayerAdded) {
		renderStoryMarkers();
	}

	onMount(async () => {
		// Load custom Maputnik style
		const styleResponse = await fetch('/map-style.json');
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

			// Add boundary line (prominent border)
			map.addLayer({
				id: 'boundary-line',
				type: 'line',
				source: 'boundary',
				paint: {
					'line-color': '#1e5a8e',
					'line-width': 5,
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
					'line-width': 7,
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
			
			// Create inner element for the emoji
			const icon = document.createElement('div');
			icon.className = 'story-marker-icon';
			icon.innerHTML = typeConfig.icon;
			icon.style.fontSize = story.type === 'project' ? '48px' : '36px';
			
			el.appendChild(icon);

			// Create marker with anchor at center-bottom
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
					? new Date(story.created_at).toLocaleDateString('nl-NL')
					: '';

				let popupHTML = `
					<div class="popup-content">
						<div class="popup-header">
							<span class="popup-icon">${typeConfig.icon}</span>
							<span class="popup-type">${escapeHtml(typeConfig.label)}</span>
						</div>
						<p class="popup-text">${escapeHtml(story.text)}</p>
				`;

				if (story.organisatie) {
					popupHTML += `<p class="popup-meta"><strong>Organisatie:</strong> ${escapeHtml(story.organisatie)}</p>`;
				}
				if (story.naam) {
					popupHTML += `<p class="popup-meta"><strong>Naam:</strong> ${escapeHtml(story.naam)}</p>`;
				}
				if (story.link) {
					const fullUrl = story.link.startsWith('http://') || story.link.startsWith('https://') 
						? story.link 
						: 'https://' + story.link;
					popupHTML += `<p class="popup-meta"><strong>Link:</strong> <a href="${escapeHtml(fullUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(story.link)}</a></p>`;
				}

				if (created) {
					popupHTML += `<small style="color: #9ca3af; font-size: 12px;">${created}</small>`;
				}

				popupHTML += `</div>`;

				new maplibregl.Popup({ offset: 25 })
					.setLngLat([story.lng, story.lat])
					.setHTML(popupHTML)
					.addTo(map);
			});

			storyMarkers.push(marker);
		});

		console.log(`✅ Rendered ${storyMarkers.length} markers on map`);
	}

	export function refreshStories(newStories: StoryWithCoords[]) {
		stories = newStories;
		renderStoryMarkers();
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

		// Create confirmation popup
		const popup = new maplibregl.Popup({ 
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

		// Handle confirmation
		setTimeout(() => {
			const confirmBtn = document.getElementById('confirm-location');
			const cancelBtn = document.getElementById('cancel-location');

			if (confirmBtn) {
				confirmBtn.onclick = () => {
					popup.remove();
					if (tempMarker) tempMarker.remove();
					dispatch('mapclick', { lng, lat });
				};
			}

			if (cancelBtn) {
				cancelBtn.onclick = () => {
					popup.remove();
					if (tempMarker) tempMarker.remove();
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
		padding: 12px;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
		min-width: 200px;
	}

	:global(.maplibregl-popup-close-button) {
		font-size: 20px;
		padding: 4px 8px;
	}

	:global(.popup-content) {
		font-family: system-ui, -apple-system, sans-serif;
	}

	:global(.popup-header) {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 8px;
		padding-bottom: 8px;
		border-bottom: 1px solid #e5e7eb;
	}

	:global(.popup-icon) {
		font-size: 20px;
	}

	:global(.popup-type) {
		font-weight: 600;
		font-size: 13px;
		color: #374151;
	}

	:global(.popup-text) {
		margin: 0 0 8px 0;
		font-size: 14px;
		line-height: 1.5;
		color: #4b5563;
	}

	:global(.popup-meta) {
		margin: 4px 0;
		font-size: 13px;
		line-height: 1.4;
		color: #6b7280;
	}

	:global(.popup-meta strong) {
		color: #374151;
		font-weight: 600;
	}

	:global(.popup-meta a) {
		color: #1e5a8e;
		text-decoration: none;
		word-break: break-all;
	}

	:global(.popup-meta a:hover) {
		text-decoration: underline;
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
	}

	:global(.story-marker-icon) {
		text-shadow: 0 0 3px white, 0 0 5px white;
		transition: transform 0.2s ease;
		transform-origin: center center;
		line-height: 1;
	}

	:global(.story-marker-wrapper:hover .story-marker-icon) {
		transform: scale(1.3);
	}
</style>


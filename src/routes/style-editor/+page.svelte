<script lang="ts">
	import { onMount } from 'svelte';
	import maplibregl from 'maplibre-gl';
	import 'maplibre-gl/dist/maplibre-gl.css';

	let mapContainer: HTMLDivElement;
	let map: maplibregl.Map;

	// Customizable colors
	let waterColor = '#1e5a8e';
	let backgroundColor = '#f5f5f0';
	let roadColor = '#ffffff';
	let buildingColor = '#e0e0e0';
	let parkColor = '#c8e6c9';
	let textColor = '#164370';

	let styles = [
		{ 
			name: 'Waterwegregio Blauw (Recommended)',
			water: '#1e5a8e',
			bg: '#f5f5f0',
			road: '#ffffff',
			building: '#e0e0e0',
			park: '#c8e6c9',
			text: '#164370'
		},
		{ 
			name: 'Soft Pastel',
			water: '#b3d9ff',
			bg: '#fff9f0',
			road: '#ffffff',
			building: '#f0e6d9',
			park: '#d4edda',
			text: '#5a6268'
		},
		{ 
			name: 'Queering the Map Style',
			water: '#ffb3ba',
			bg: '#fff5f5',
			road: '#ffffff',
			building: '#ffe4e1',
			park: '#bae1ba',
			text: '#c06c84'
		},
		{ 
			name: 'Dark Mode',
			water: '#4a90e2',
			bg: '#2d3436',
			road: '#636e72',
			building: '#4a5568',
			park: '#48bb78',
			text: '#e2e8f0'
		},
		{ 
			name: 'Minimal Gray',
			water: '#a8a8a8',
			bg: '#fafafa',
			road: '#ffffff',
			building: '#d8d8d8',
			park: '#e8e8e8',
			text: '#424242'
		}
	];

	onMount(() => {
		map = new maplibregl.Map({
			container: mapContainer,
			style: createCustomStyle(),
			center: [4.4, 51.9],
			zoom: 11
		});

		map.addControl(new maplibregl.NavigationControl(), 'top-right');
	});

	function createCustomStyle() {
		return {
			version: 8,
			glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
			sources: {
				'osm-raster': {
					type: 'raster',
					tiles: [
						'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
					],
					tileSize: 256,
					attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				}
			},
			layers: [
				{
					id: 'background',
					type: 'background',
					paint: {
						'background-color': backgroundColor
					}
				},
				{
					id: 'osm-tiles',
					type: 'raster',
					source: 'osm-raster',
					paint: {
						'raster-opacity': 0.6,
						'raster-saturation': -0.3,
						'raster-brightness-min': 0.3,
						'raster-brightness-max': 0.9
					}
				}
			]
		};
	}

	function updateMapStyle() {
		if (map) {
			map.setStyle(createCustomStyle());
		}
	}

	function applyPreset(preset: typeof styles[0]) {
		waterColor = preset.water;
		backgroundColor = preset.bg;
		roadColor = preset.road;
		buildingColor = preset.building;
		parkColor = preset.park;
		textColor = preset.text;
		updateMapStyle();
	}

	function exportStyle() {
		const style = createCustomStyle();
		const blob = new Blob([JSON.stringify(style, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = 'waterwegregio-style.json';
		a.click();
		URL.revokeObjectURL(url);
	}

	function copyStyleCode() {
		const code = `// Paste this in Map.svelte
style: {
	version: 8,
	glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
	sources: {
		'osm-raster': {
			type: 'raster',
			tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
			tileSize: 256,
			attribution: '&copy; OpenStreetMap contributors'
		}
	},
	layers: [
		{
			id: 'background',
			type: 'background',
			paint: { 'background-color': '${backgroundColor}' }
		},
		{
			id: 'osm-tiles',
			type: 'raster',
			source: 'osm-raster',
			paint: {
				'raster-opacity': 0.6,
				'raster-saturation': -0.3,
				'raster-brightness-min': 0.3,
				'raster-brightness-max': 0.9
			}
		}
	]
}`;
		navigator.clipboard.writeText(code);
		alert('Code gekopieerd! Plak in Map.svelte');
	}
</script>

<svelte:head>
	<title>Map Style Editor - Waterwegregio</title>
</svelte:head>

<div class="style-editor">
	<div class="sidebar">
		<div class="header">
			<h1>🎨 Map Style Editor</h1>
			<a href="/" class="back-link">← Terug naar kaart</a>
		</div>

		<div class="section">
			<h2>Presets</h2>
			{#each styles as preset}
				<button class="preset-btn" on:click={() => applyPreset(preset)}>
					{preset.name}
				</button>
			{/each}
		</div>

		<div class="section">
			<h2>Custom Colors</h2>
			
			<div class="color-group">
				<label>
					Background
					<input type="color" bind:value={backgroundColor} on:change={updateMapStyle} />
					<code>{backgroundColor}</code>
				</label>
			</div>

			<div class="color-group">
				<label>
					Water
					<input type="color" bind:value={waterColor} on:change={updateMapStyle} />
					<code>{waterColor}</code>
				</label>
			</div>

			<div class="color-group">
				<label>
					Roads
					<input type="color" bind:value={roadColor} on:change={updateMapStyle} />
					<code>{roadColor}</code>
				</label>
			</div>

			<div class="color-group">
				<label>
					Buildings
					<input type="color" bind:value={buildingColor} on:change={updateMapStyle} />
					<code>{buildingColor}</code>
				</label>
			</div>

			<div class="color-group">
				<label>
					Parks
					<input type="color" bind:value={parkColor} on:change={updateMapStyle} />
					<code>{parkColor}</code>
				</label>
			</div>

			<div class="color-group">
				<label>
					Text
					<input type="color" bind:value={textColor} on:change={updateMapStyle} />
					<code>{textColor}</code>
				</label>
			</div>
		</div>

		<div class="section actions">
			<button class="action-btn primary" on:click={copyStyleCode}>
				📋 Copy Style Code
			</button>
			<button class="action-btn secondary" on:click={exportStyle}>
				💾 Export JSON
			</button>
		</div>

		<div class="info">
			<p>💡 <strong>Tip:</strong> Voor een custom vector tile style zoals Queering the Map, gebruik <a href="https://maputnik.github.io/" target="_blank">Maputnik</a></p>
		</div>
	</div>

	<div class="map-preview">
		<div bind:this={mapContainer} class="map"></div>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.style-editor {
		display: flex;
		height: 100vh;
		overflow: hidden;
	}

	.sidebar {
		width: 350px;
		background: #ffffff;
		border-right: 1px solid #e5e7eb;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
	}

	.header {
		padding: 24px;
		border-bottom: 1px solid #e5e7eb;
		background: linear-gradient(135deg, #1e5a8e 0%, #164370 100%);
		color: white;
	}

	.header h1 {
		margin: 0 0 12px 0;
		font-size: 22px;
		font-weight: 600;
	}

	.back-link {
		color: white;
		text-decoration: none;
		font-size: 14px;
		opacity: 0.9;
		display: inline-block;
		margin-top: 8px;
	}

	.back-link:hover {
		opacity: 1;
		text-decoration: underline;
	}

	.section {
		padding: 24px;
		border-bottom: 1px solid #f3f4f6;
	}

	.section h2 {
		margin: 0 0 16px 0;
		font-size: 16px;
		font-weight: 600;
		color: #111827;
	}

	.preset-btn {
		width: 100%;
		padding: 12px;
		margin-bottom: 8px;
		border: 1px solid #d1d5db;
		background: white;
		border-radius: 8px;
		font-size: 14px;
		cursor: pointer;
		transition: all 0.2s;
		text-align: left;
	}

	.preset-btn:hover {
		background: #f9fafb;
		border-color: #1e5a8e;
	}

	.color-group {
		margin-bottom: 16px;
	}

	.color-group label {
		display: flex;
		align-items: center;
		gap: 12px;
		font-size: 14px;
		font-weight: 500;
		color: #374151;
	}

	.color-group input[type="color"] {
		width: 50px;
		height: 35px;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		cursor: pointer;
	}

	.color-group code {
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 12px;
		color: #6b7280;
		background: #f3f4f6;
		padding: 4px 8px;
		border-radius: 4px;
	}

	.actions {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.action-btn {
		padding: 12px 20px;
		border: none;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.action-btn.primary {
		background: #1e5a8e;
		color: white;
	}

	.action-btn.primary:hover {
		background: #164370;
	}

	.action-btn.secondary {
		background: #e5e7eb;
		color: #374151;
	}

	.action-btn.secondary:hover {
		background: #d1d5db;
	}

	.info {
		padding: 16px 24px;
		background: #eff6ff;
		border-top: 1px solid #e5e7eb;
		font-size: 13px;
		line-height: 1.6;
		color: #374151;
	}

	.info a {
		color: #1e5a8e;
		text-decoration: none;
	}

	.info a:hover {
		text-decoration: underline;
	}

	.map-preview {
		flex: 1;
		position: relative;
	}

	.map {
		width: 100%;
		height: 100%;
	}

	@media (max-width: 768px) {
		.style-editor {
			flex-direction: column;
		}

		.sidebar {
			width: 100%;
			height: 50vh;
		}

		.map-preview {
			height: 50vh;
		}
	}
</style>


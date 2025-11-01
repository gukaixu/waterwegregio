<script lang="ts">
	import { onMount } from 'svelte';
	import Map from '$lib/components/Map.svelte';
	import SubmissionModal from '$lib/components/SubmissionModal.svelte';
	import { supabase } from '$lib/supabase';
	import type { StoryWithCoords } from '$lib/supabase';
	import 'maplibre-gl/dist/maplibre-gl.css';

	let stories: StoryWithCoords[] = [];
	let mapComponent: Map;
	let showModal = false;
	let selectedLat: number | null = null;
	let selectedLng: number | null = null;
	let showInstructions = true;
	let showBoundaryWarning = false;

	onMount(async () => {
		await loadStories();
	});

	async function loadStories() {
		try {
			console.log('📍 Loading stories from Supabase...');
			const { data, error } = await supabase
				.from('stories_with_coords')
				.select('*')
				.eq('status', 'approved')
				.order('created_at', { ascending: false});

			if (error) {
				console.error('❌ Error loading stories:', error);
				return;
			}

			console.log(`✓ Loaded ${data?.length || 0} stories from database`);
			console.log('Stories with coordinates:', data);

			stories = (data || []) as StoryWithCoords[];
			console.log(`✓ Total stories with valid coordinates: ${stories.length}`);
		} catch (error) {
			console.error('❌ Error loading stories:', error);
		}
	}

	function handleMapClick(event: CustomEvent<{ lat: number; lng: number }>) {
		selectedLat = event.detail.lat;
		selectedLng = event.detail.lng;
		showModal = true;
		showInstructions = false;
		showBoundaryWarning = false;
	}

	function handleOutsideBoundary() {
		showBoundaryWarning = true;
		showInstructions = false;
		setTimeout(() => {
			showBoundaryWarning = false;
			showInstructions = true;
		}, 3000);
	}

	async function handleSubmissionSuccess() {
		await loadStories();
		if (mapComponent) {
			mapComponent.refreshStories(stories);
		}
		showInstructions = true;
	}
</script>

<svelte:head>
	<title>Waterwegregio Verhalen Kaart</title>
	<meta name="description" content="Deel je verhalen, ervaringen en herinneringen uit de Waterwegregio" />
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap" rel="stylesheet">
</svelte:head>

<div class="app">
	<main class="main-content">
		<Map bind:this={mapComponent} {stories} on:mapclick={handleMapClick} on:outsideboundary={handleOutsideBoundary} />

		<!-- Simple centered title -->
		<div class="map-title">
			<h1>WATERWEGREGIO VERHALENKAART</h1>
		</div>

		{#if showInstructions}
			<div class="instructions">
				<p>📍 Klik op de kaart om je verhaal te plaatsen</p>
			</div>
		{/if}

		{#if showBoundaryWarning}
			<div class="boundary-warning">
				<p>⚠️ Je kunt alleen verhalen plaatsen binnen de Waterwegregio (het blauwe gebied)</p>
			</div>
		{/if}
	</main>

	<SubmissionModal
		bind:isOpen={showModal}
		lat={selectedLat}
		lng={selectedLng}
		on:success={handleSubmissionSuccess}
		on:close={() => {
			showInstructions = false;
		}}
	/>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
			Arial, sans-serif;
		overflow: hidden;
	}

	.app {
		height: 100vh;
		width: 100vw;
		overflow: hidden;
	}

	.main-content {
		position: relative;
		width: 100%;
		height: 100%;
	}

	.map-title {
		position: absolute;
		top: 30px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 10;
		pointer-events: none;
	}

	.map-title h1 {
		margin: 0;
		font-size: 32px;
		font-weight: 700;
		font-family: 'Roboto Condensed', sans-serif;
		color: #1e5a8e;
		text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.9),
		             -1px -1px 2px rgba(255, 255, 255, 0.9),
		             1px -1px 2px rgba(255, 255, 255, 0.9),
		             -1px 1px 2px rgba(255, 255, 255, 0.9);
		white-space: nowrap;
		letter-spacing: 1px;
	}

	.instructions {
		position: absolute;
		bottom: 30px;
		left: 50%;
		transform: translateX(-50%);
		background: white;
		padding: 12px 24px;
		border-radius: 24px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		z-index: 5;
		animation: bounce 2s ease-in-out infinite;
	}

	.instructions p {
		margin: 0;
		font-size: 14px;
		font-weight: 500;
		color: #374151;
	}

	@keyframes bounce {
		0%,
		100% {
			transform: translateX(-50%) translateY(0);
		}
		50% {
			transform: translateX(-50%) translateY(-5px);
		}
	}

	.boundary-warning {
		position: absolute;
		bottom: 30px;
		left: 50%;
		transform: translateX(-50%);
		background: #fef3c7;
		border: 2px solid #f59e0b;
		color: #92400e;
		padding: 12px 24px;
		border-radius: 24px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		z-index: 5;
		max-width: 90%;
	}

	.boundary-warning p {
		margin: 0;
		font-size: 14px;
		font-weight: 500;
	}

	@media (max-width: 768px) {
		.map-title {
			top: 20px;
		}

		.map-title h1 {
			font-size: 20px;
		}

		.instructions {
			bottom: 20px;
			left: 10px;
			right: 10px;
			transform: none;
			text-align: center;
		}

		.boundary-warning {
			bottom: 20px;
			left: 10px;
			right: 10px;
			transform: none;
			text-align: center;
		}

		.boundary-warning p {
			font-size: 13px;
		}
	}
</style>

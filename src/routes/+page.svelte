<script lang="ts">
	import { onMount } from 'svelte';
	import Map from '$lib/components/Map.svelte';
	import SubmissionModal from '$lib/components/SubmissionModal.svelte';
	import Toast from '$lib/components/Toast.svelte';
	import { supabase } from '$lib/supabase';
	import type { StoryWithCoords } from '$lib/supabase';
	import { toastStore } from '$lib/stores/toastStore';
	import 'maplibre-gl/dist/maplibre-gl.css';

	let stories: StoryWithCoords[] = [];
	let mapComponent: Map;
	let showModal = false;
	let selectedLat: number | null = null;
	let selectedLng: number | null = null;
	let showInstructions = true;
	let showBoundaryWarning = false;
	let isAdmin = false;

	// Admin password (in production, use environment variable)
	const ADMIN_PASSWORD = 'waterwegregio2024';

	function toggleAdmin() {
		if (isAdmin) {
			isAdmin = false;
			toastStore.show('Admin modus uitgeschakeld', 'info');
		} else {
			const password = prompt('Voer admin wachtwoord in:');
			if (password === ADMIN_PASSWORD) {
				isAdmin = true;
				toastStore.show('Admin modus ingeschakeld', 'success');
			} else if (password !== null) {
				toastStore.show('Onjuist wachtwoord', 'error');
			}
		}
	}

	onMount(async () => {
		await loadStories();
	});

	let isLoadingStories = true;
	
	async function loadStories() {
		try {
			isLoadingStories = true;
			console.log('📍 Loading stories from Supabase...');
			const { data, error } = await supabase
				.from('stories_with_coords')
				.select('*')
				.eq('status', 'approved')
				.order('created_at', { ascending: false});

			if (error) {
				console.error('❌ Error loading stories:', error);
				toastStore.show('Fout bij laden van verhalen', 'error');
				return;
			}

			console.log(`✓ Loaded ${data?.length || 0} stories from database`);
			console.log('Stories with coordinates:', data);

			stories = (data || []) as StoryWithCoords[];
			console.log(`✓ Total stories with valid coordinates: ${stories.length}`);
		} catch (error) {
			console.error('❌ Error loading stories:', error);
			toastStore.show('Fout bij laden van verhalen', 'error');
		} finally {
			isLoadingStories = false;
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
	<link href="https://fonts.googleapis.com/css2?family=Amatic+SC:wght@700&family=Fredoka:wght@600&display=swap" rel="stylesheet">
</svelte:head>

<div class="app">
	<main class="main-content">
		<Map bind:this={mapComponent} {stories} on:mapclick={handleMapClick} on:outsideboundary={handleOutsideBoundary} />

		<!-- Title with Monster logo -->
		<div class="map-title">
			<img src="/monster-logo.png" alt="Monster Logo" class="monster-logo" />
			<h1>Waterwegregio Verhalenkaart</h1>
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

		<!-- Regiodeal Waterwegregio Logo -->
		<a href="https://www.regiodealwaterwegregio.nl" target="_blank" rel="noopener noreferrer" class="regiodeal-logo-link">
			<img src="/wwr-logo.jpeg" alt="Regiodeal Waterwegregio" class="regiodeal-logo" />
		</a>

		<!-- Admin Toggle Button -->
		<button class="admin-toggle" on:click={toggleAdmin} class:active={isAdmin} title={isAdmin ? 'Admin modus' : 'Admin login'}>
			🔑
		</button>
	</main>

	<SubmissionModal
		bind:isOpen={showModal}
		lat={selectedLat}
		lng={selectedLng}
		isAdmin={isAdmin}
		on:success={handleSubmissionSuccess}
		on:close={() => {
			showInstructions = false;
		}}
	/>

	<!-- Toast notifications -->
	{#each $toastStore as toast (toast.id)}
		<Toast
			message={toast.message}
			type={toast.type}
			duration={toast.duration}
			onClose={() => toastStore.remove(toast.id)}
		/>
	{/each}
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
		top: 20px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 10;
		pointer-events: none;
		display: flex;
		align-items: center;
		gap: 16px;
	}

	.monster-logo {
		width: auto;
		height: 50px;
		object-fit: contain;
		/* Darker navy color filter - toned down */
		filter: brightness(0) saturate(100%) invert(22%) sepia(55%) saturate(900%) hue-rotate(186deg) brightness(80%) contrast(85%) drop-shadow(0 2px 6px rgba(255, 255, 255, 0.9));
	}

	.map-title h1 {
		margin: 0;
		font-size: 42px;
		font-weight: 700;
		font-family: 'Amatic SC', cursive;
		color: #1e5a8e;
		text-shadow: 3px 3px 0px rgba(255, 255, 255, 0.95),
		             -2px -2px 0px rgba(255, 255, 255, 0.95),
		             2px -2px 0px rgba(255, 255, 255, 0.95),
		             -2px 2px 0px rgba(255, 255, 255, 0.95),
		             0 4px 8px rgba(255, 255, 255, 0.7);
		white-space: nowrap;
		letter-spacing: 0.5px;
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

	.regiodeal-logo-link {
		position: absolute;
		bottom: 20px;
		left: 20px;
		z-index: 10;
		transition: transform 0.3s ease, opacity 0.3s ease;
		opacity: 0.9;
	}

	.regiodeal-logo-link:hover {
		transform: scale(1.05);
		opacity: 1;
	}

	.regiodeal-logo {
		height: 90px;
		width: auto;
		object-fit: contain;
		border-radius: 8px;
		background: white;
		padding: 10px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.admin-toggle {
		position: absolute;
		top: 20px;
		right: 70px;
		z-index: 10;
		background: white;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		width: 40px;
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 20px;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.admin-toggle:hover {
		background: #f3f4f6;
		transform: scale(1.05);
	}

	.admin-toggle.active {
		background: linear-gradient(135deg, #7c3aed, #dc2626);
		border-color: transparent;
		box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
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

		.regiodeal-logo-link {
			bottom: 80px;
			left: 10px;
		}

		.regiodeal-logo {
			height: 60px;
			padding: 8px;
		}

		.admin-toggle {
			top: 10px;
			right: 10px;
			width: 36px;
			height: 36px;
			font-size: 18px;
		}
	}
</style>

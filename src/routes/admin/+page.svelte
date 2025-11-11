<script lang="ts">
	import { onMount } from 'svelte';
	import { supabase, storyTypes } from '$lib/supabase';
	import type { StoryWithCoords } from '$lib/supabase';

	let isAuthenticated = false;
	let password = '';
	let loginError = '';
	let stories: StoryWithCoords[] = [];
	let loading = true;
	let searchTerm = '';

	// Simple client-side password check for MVP
	// In production, use proper server-side authentication
	const ADMIN_PASSWORD = 'resilientdelta2025';

	onMount(async () => {
		// Check if already authenticated in session
		const auth = sessionStorage.getItem('admin_auth');
		if (auth === 'true') {
			isAuthenticated = true;
			await loadStories();
		} else {
			loading = false;
		}
	});

	async function handleLogin() {
		if (password === ADMIN_PASSWORD) {
			isAuthenticated = true;
			sessionStorage.setItem('admin_auth', 'true');
			loginError = '';
			await loadStories();
		} else {
			loginError = 'Onjuist wachtwoord';
		}
	}

	async function loadStories() {
		loading = true;
		try {
			const { data, error } = await supabase
				.from('stories_with_coords')
				.select('*')
				.order('created_at', { ascending: false });

			if (error) {
				console.error('Error loading stories:', error);
				alert('Fout bij laden verhalen: ' + error.message);
				return;
			}

			stories = (data || []) as StoryWithCoords[];
		} catch (error) {
			console.error('Error loading stories:', error);
		} finally {
			loading = false;
		}
	}

	async function deleteStory(id: string, text: string) {
		const preview = text.substring(0, 50) + (text.length > 50 ? '...' : '');
		if (!confirm(`Weet je zeker dat je dit verhaal wilt verwijderen?\n\n"${preview}"`)) {
			return;
		}

		try {
			const response = await fetch('/api/delete-story', {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ id })
			});

			const result = await response.json();

			if (!response.ok) {
				throw new Error(result.error || 'Er is een fout opgetreden');
			}

			// Remove from local state immediately
			stories = stories.filter(s => s.id !== id);
			
			// Reload to confirm
			await loadStories();
		} catch (error) {
			console.error('Error deleting story:', error);
			alert(error instanceof Error ? error.message : 'Fout bij verwijderen verhaal');
		}
	}

	function handleLogout() {
		sessionStorage.removeItem('admin_auth');
		isAuthenticated = false;
		password = '';
		stories = [];
	}

	$: if (isAuthenticated) {
		loadStories();
	}

	$: filteredStories = stories.filter(story => 
		story.text.toLowerCase().includes(searchTerm.toLowerCase())
	);
</script>

<svelte:head>
	<title>Beheer - Waterwegregio Verhalen Kaart</title>
</svelte:head>

<div class="admin-page">
	<header>
		<div class="header-content">
			<div class="header-left-admin">
				<img src="/logo-waterwegregio.svg" alt="Regiodeal Waterwegregio" class="logo" />
				<div>
					<h1>Beheer Verhalen</h1>
					<p class="subtitle">Waterwegregio Verhalen Kaart</p>
				</div>
			</div>
			<div class="header-actions">
				<a href="/" class="link-button">← Terug naar kaart</a>
				{#if isAuthenticated}
					<button class="btn btn-secondary" on:click={handleLogout}>Uitloggen</button>
				{/if}
			</div>
		</div>
	</header>

	<main>
		{#if !isAuthenticated}
			<div class="login-container">
				<div class="login-box">
					<h2>Inloggen</h2>
					<form on:submit|preventDefault={handleLogin}>
						<div class="form-group">
							<label for="password">Wachtwoord</label>
							<input
								id="password"
								type="password"
								bind:value={password}
								placeholder="Voer wachtwoord in"
								autocomplete="current-password"
							/>
						</div>
						{#if loginError}
							<div class="error-message">{loginError}</div>
						{/if}
						<button type="submit" class="btn btn-primary">Inloggen</button>
					</form>
				</div>
			</div>
		{:else}
			<div class="content-container">
				<div class="toolbar">
					<div class="stats">
						<span class="total-count">Totaal: {stories.length} verhalen</span>
					</div>
					<input
						type="text"
						bind:value={searchTerm}
						placeholder="Zoek verhaal..."
						class="search-input"
					/>
				</div>

				{#if loading}
					<div class="loading">Laden...</div>
				{:else if filteredStories.length === 0}
					<div class="empty-state">
						<p>{searchTerm ? 'Geen verhalen gevonden met deze zoekterm' : 'Geen verhalen gevonden'}</p>
					</div>
				{:else}
					<div class="stories-list">
						{#each filteredStories as story (story.id)}
							<div class="story-card">
								<div class="story-header">
									<div class="story-meta">
										<span class="type-badge">
											<img src={storyTypes[story.type]?.icon || storyTypes.bewoner.icon} alt={story.type} class="type-icon-small" />
											{story.type}
										</span>
										<span class="date">
											{new Date(story.created_at).toLocaleString('nl-NL')}
										</span>
									</div>
									<div class="story-location">
										📍 {story.lat.toFixed(4)}, {story.lng.toFixed(4)}
									</div>
								</div>

								<div class="story-content">
									<p class="story-text">{story.text}</p>
									{#if story.organisatie || story.naam || story.link}
										<div class="story-metadata">
											{#if story.organisatie}
												<p><strong>Organisatie:</strong> {story.organisatie}</p>
											{/if}
											{#if story.naam}
												<p><strong>Naam:</strong> {story.naam}</p>
											{/if}
											{#if story.link}
												<p><strong>Link:</strong> <a href={story.link.startsWith('http://') || story.link.startsWith('https://') ? story.link : 'https://' + story.link} target="_blank" rel="noopener noreferrer">{story.link}</a></p>
											{/if}
										</div>
									{/if}
								</div>

								<div class="story-actions">
									<button class="btn btn-delete" on:click={() => deleteStory(story.id, story.text)}>
										🗑️ Verwijderen
									</button>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
			Arial, sans-serif;
		background: #f9fafb;
	}

	.admin-page {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	header {
		background: linear-gradient(135deg, #1e5a8e 0%, #164370 100%);
		color: white;
		padding: 24px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.header-content {
		max-width: 1400px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.header-left-admin {
		display: flex;
		align-items: center;
		gap: 20px;
	}

	.logo {
		height: 50px;
		width: auto;
	}

	.header-content h1 {
		margin: 0;
		font-size: 28px;
		font-weight: 600;
	}

	.subtitle {
		margin: 4px 0 0 0;
		font-size: 14px;
		opacity: 0.9;
	}

	.header-actions {
		display: flex;
		gap: 12px;
	}

	.link-button {
		color: white;
		text-decoration: none;
		padding: 10px 20px;
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 6px;
		font-size: 14px;
		transition: all 0.2s;
		display: inline-block;
	}

	.link-button:hover {
		background: rgba(255, 255, 255, 0.1);
		border-color: rgba(255, 255, 255, 0.5);
	}

	main {
		flex: 1;
	}

	.login-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: calc(100vh - 120px);
		padding: 20px;
	}

	.login-box {
		background: white;
		padding: 40px;
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		max-width: 400px;
		width: 100%;
	}

	.login-box h2 {
		margin: 0 0 24px 0;
		font-size: 24px;
		color: #111827;
	}

	.form-group {
		margin-bottom: 20px;
	}

	label {
		display: block;
		margin-bottom: 8px;
		font-weight: 500;
		color: #374151;
		font-size: 14px;
	}

	input {
		width: 100%;
		padding: 12px;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-size: 14px;
		font-family: inherit;
		box-sizing: border-box;
	}

	input:focus {
		outline: none;
		border-color: #1e5a8e;
		box-shadow: 0 0 0 3px rgba(30, 90, 142, 0.1);
	}

	.content-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 32px 24px;
	}

	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24px;
		gap: 20px;
		flex-wrap: wrap;
	}

	.stats {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	.total-count {
		font-size: 18px;
		font-weight: 600;
		color: #111827;
	}

	.search-input {
		padding: 10px 16px;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-size: 14px;
		min-width: 250px;
		font-family: inherit;
	}

	.search-input:focus {
		outline: none;
		border-color: #1e5a8e;
		box-shadow: 0 0 0 3px rgba(30, 90, 142, 0.1);
	}

	.loading,
	.empty-state {
		text-align: center;
		padding: 60px 20px;
		color: #6b7280;
	}

	.stories-list {
		display: grid;
		gap: 20px;
	}

	.story-card {
		background: white;
		border-radius: 12px;
		padding: 24px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		border: 1px solid #e5e7eb;
		transition: all 0.2s;
	}

	.story-card:hover {
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.story-header {
		display: flex;
		justify-content: space-between;
		align-items: start;
		margin-bottom: 16px;
		flex-wrap: wrap;
		gap: 12px;
	}

	.story-meta {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}

	.type-badge {
		padding: 4px 12px;
		border-radius: 12px;
		font-size: 12px;
		font-weight: 500;
		background: #f3f4f6;
		color: #374151;
		text-transform: capitalize;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}

	.type-icon-small {
		width: auto;
		height: 20px;
		object-fit: contain;
		/* Navy color filter */
		filter: brightness(0) saturate(100%) invert(28%) sepia(65%) saturate(1234%) hue-rotate(186deg) brightness(93%) contrast(88%);
	}
	
	/* Toned down orange project puzzle piece */
	.type-icon-small[src*="projectpuzzelstuk"] {
		filter: brightness(0) saturate(100%) invert(55%) sepia(85%) saturate(2200%) hue-rotate(1deg) brightness(95%) contrast(98%) !important;
	}

	.date {
		font-size: 13px;
		color: #6b7280;
	}

	.story-location {
		font-size: 13px;
		color: #6b7280;
		font-family: monospace;
	}

	.story-content {
		margin-bottom: 20px;
	}

	.story-text {
		margin: 0 0 12px 0;
		color: #111827;
		line-height: 1.6;
	}

	.story-metadata {
		padding: 12px;
		background: #f9fafb;
		border-radius: 6px;
		margin-top: 8px;
	}

	.story-metadata p {
		margin: 4px 0;
		font-size: 13px;
		color: #6b7280;
		line-height: 1.4;
	}

	.story-metadata strong {
		color: #374151;
		font-weight: 600;
	}

	.story-metadata a {
		color: #1e5a8e;
		text-decoration: none;
		word-break: break-all;
	}

	.story-metadata a:hover {
		text-decoration: underline;
	}

	.story-actions {
		display: flex;
		gap: 12px;
		flex-wrap: wrap;
		justify-content: flex-end;
	}

	.btn {
		padding: 8px 16px;
		border: none;
		border-radius: 6px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
	}

	.btn-primary {
		background: #1e5a8e;
		color: white;
		width: 100%;
	}

	.btn-primary:hover {
		background: #164370;
	}

	.btn-secondary {
		background: #e5e7eb;
		color: #374151;
	}

	.btn-secondary:hover {
		background: #d1d5db;
	}

	.btn-delete {
		background: #ef4444;
		color: white;
	}

	.btn-delete:hover {
		background: #dc2626;
	}

	.error-message {
		padding: 12px;
		background: #fee2e2;
		border: 1px solid #fecaca;
		border-radius: 8px;
		color: #dc2626;
		font-size: 14px;
		margin-bottom: 20px;
	}

	@media (max-width: 768px) {
		.header-content {
			flex-direction: column;
			align-items: flex-start;
			gap: 16px;
		}

		.header-left-admin {
			gap: 12px;
		}

		.logo {
			height: 40px;
		}

		.header-content h1 {
			font-size: 22px;
		}

		.header-actions {
			width: 100%;
			justify-content: space-between;
		}

		.story-header {
			flex-direction: column;
		}

		.story-actions {
			flex-direction: column;
		}

		.story-actions .btn {
			width: 100%;
		}
	}
</style>


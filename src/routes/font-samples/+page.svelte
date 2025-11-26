<script lang="ts">
	const fontSamples = [
		{
			name: 'Caveat (Current)',
			family: 'Caveat',
			weight: '700',
			description: 'Playful, handwritten - currently in use'
		},
		{
			name: 'Pacifico',
			family: 'Pacifico',
			weight: '400',
			description: 'Friendly, relaxed script with personality'
		},
		{
			name: 'Fredoka',
			family: 'Fredoka',
			weight: '600',
			description: 'Rounded, modern, approachable and playful'
		},
		{
			name: 'Righteous',
			family: 'Righteous',
			weight: '400',
			description: 'Bold, quirky, stands out without being too playful'
		},
		{
			name: 'Comfortaa',
			family: 'Comfortaa',
			weight: '700',
			description: 'Soft, rounded, comfortable and friendly'
		},
		{
			name: 'Satisfy',
			family: 'Satisfy',
			weight: '400',
			description: 'Elegant handwritten script, more sophisticated'
		},
		{
			name: 'Permanent Marker',
			family: 'Permanent Marker',
			weight: '400',
			description: 'Bold marker style, casual and authentic'
		},
		{
			name: 'Amatic SC',
			family: 'Amatic SC',
			weight: '700',
			description: 'Hand-drawn, artistic, community feel'
		},
		{
			name: 'Raleway',
			family: 'Raleway',
			weight: '800',
			description: 'Clean, modern, professional yet friendly'
		},
		{
			name: 'Kalam',
			family: 'Kalam',
			weight: '700',
			description: 'Natural handwriting, authentic and personal'
		}
	];

	let selectedFont = 'Caveat';
</script>

<svelte:head>
	<title>Font Samples - Waterwegregio</title>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Pacifico&family=Fredoka:wght@600&family=Righteous&family=Comfortaa:wght@700&family=Satisfy&family=Permanent+Marker&family=Amatic+SC:wght@700&family=Raleway:wght@800&family=Kalam:wght@700&display=swap" rel="stylesheet">
</svelte:head>

<div class="container">
	<header class="page-header">
		<h1>Font Samples voor Waterwegregio Verhalenkaart</h1>
		<p>Klik op een font om het in het voorbeeld te zien</p>
		<a href="/" class="back-link">← Terug naar de kaart</a>
	</header>

	<div class="preview-section">
		<h2>Live Preview</h2>
		<div class="preview-card">
			<div class="title-preview" style="font-family: '{selectedFont}', cursive;">
				<img src="/monster-logo.png" alt="Monster Logo" class="monster-logo" />
				<h1>Waterwegregio Verhalenkaart</h1>
			</div>
		</div>
	</div>

	<div class="samples-grid">
		{#each fontSamples as sample}
			<button
				class="font-card"
				class:selected={selectedFont === sample.family}
				on:click={() => selectedFont = sample.family}
			>
				<div class="font-name-header">
					<h3>{sample.name}</h3>
					{#if selectedFont === sample.family}
						<span class="selected-badge">✓ Selected</span>
					{/if}
				</div>
				<p class="font-description">{sample.description}</p>
				<div 
					class="font-display" 
					style="font-family: '{sample.family}', cursive; font-weight: {sample.weight};"
				>
					Waterwegregio Verhalenkaart
				</div>
				<div class="font-meta">
					<span>Font: {sample.family}</span>
					<span>Weight: {sample.weight}</span>
				</div>
			</button>
		{/each}
	</div>

	<div class="usage-note">
		<h3>💡 Implementation Tip</h3>
		<p>To use your selected font, update the Google Fonts link in <code>+page.svelte</code> and change the <code>font-family</code> in the CSS for <code>.map-title h1</code></p>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		background: #f9fafb;
	}

	.container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 40px 20px;
	}

	.page-header {
		text-align: center;
		margin-bottom: 48px;
	}

	.page-header h1 {
		font-size: 36px;
		color: #111827;
		margin: 0 0 12px 0;
	}

	.page-header p {
		font-size: 18px;
		color: #6b7280;
		margin: 0 0 24px 0;
	}

	.back-link {
		display: inline-block;
		padding: 10px 20px;
		background: #1e5a8e;
		color: white;
		text-decoration: none;
		border-radius: 8px;
		font-weight: 500;
		transition: all 0.3s ease;
	}

	.back-link:hover {
		background: #164370;
		transform: translateY(-1px);
		box-shadow: 0 4px 12px rgba(30, 90, 142, 0.3);
	}

	.preview-section {
		margin-bottom: 48px;
	}

	.preview-section h2 {
		font-size: 24px;
		color: #111827;
		margin: 0 0 20px 0;
		text-align: center;
	}

	.preview-card {
		background: white;
		border-radius: 16px;
		padding: 48px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
	}

	.title-preview {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 16px;
	}

	.monster-logo {
		width: auto;
		height: 50px;
		object-fit: contain;
		filter: brightness(0) saturate(100%) invert(22%) sepia(55%) saturate(900%) hue-rotate(186deg) brightness(80%) contrast(85%) drop-shadow(0 2px 6px rgba(255, 255, 255, 0.9));
	}

	.title-preview h1 {
		margin: 0;
		font-size: 42px;
		font-weight: 700;
		color: #1e5a8e;
		text-shadow: 3px 3px 0px rgba(255, 255, 255, 0.95),
					 -2px -2px 0px rgba(255, 255, 255, 0.95),
					 2px -2px 0px rgba(255, 255, 255, 0.95),
					 -2px 2px 0px rgba(255, 255, 255, 0.95),
					 0 4px 8px rgba(255, 255, 255, 0.7);
		white-space: nowrap;
		letter-spacing: 0.5px;
	}

	.samples-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
		gap: 24px;
		margin-bottom: 48px;
	}

	.font-card {
		background: white;
		border: 3px solid #e5e7eb;
		border-radius: 12px;
		padding: 24px;
		cursor: pointer;
		transition: all 0.3s ease;
		text-align: left;
		display: flex;
		flex-direction: column;
		gap: 16px;
	}

	.font-card:hover {
		border-color: #1e5a8e;
		transform: translateY(-4px);
		box-shadow: 0 8px 24px rgba(30, 90, 142, 0.2);
	}

	.font-card.selected {
		border-color: #1e5a8e;
		background: #eff6ff;
		box-shadow: 0 4px 16px rgba(30, 90, 142, 0.15);
	}

	.font-name-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
	}

	.font-name-header h3 {
		margin: 0;
		font-size: 20px;
		color: #111827;
	}

	.selected-badge {
		background: #1e5a8e;
		color: white;
		padding: 4px 12px;
		border-radius: 12px;
		font-size: 12px;
		font-weight: 600;
	}

	.font-description {
		margin: 0;
		font-size: 14px;
		color: #6b7280;
		line-height: 1.5;
	}

	.font-display {
		font-size: 32px;
		color: #1e5a8e;
		padding: 20px;
		background: #f9fafb;
		border-radius: 8px;
		text-align: center;
		border: 2px dashed #e5e7eb;
	}

	.font-meta {
		display: flex;
		justify-content: space-between;
		font-size: 12px;
		color: #9ca3af;
		padding-top: 12px;
		border-top: 1px solid #e5e7eb;
	}

	.usage-note {
		background: #fef3c7;
		border: 2px solid #fbbf24;
		border-radius: 12px;
		padding: 24px;
		text-align: center;
	}

	.usage-note h3 {
		margin: 0 0 12px 0;
		color: #92400e;
		font-size: 18px;
	}

	.usage-note p {
		margin: 0;
		color: #78350f;
		line-height: 1.6;
	}

	.usage-note code {
		background: rgba(255, 255, 255, 0.5);
		padding: 2px 6px;
		border-radius: 4px;
		font-family: 'Monaco', 'Courier New', monospace;
		font-size: 13px;
	}

	@media (max-width: 768px) {
		.container {
			padding: 20px 16px;
		}

		.page-header h1 {
			font-size: 28px;
		}

		.title-preview h1 {
			font-size: 24px;
		}

		.monster-logo {
			height: 32px;
		}

		.samples-grid {
			grid-template-columns: 1fr;
		}

		.preview-card {
			padding: 24px;
		}

		.title-preview {
			flex-direction: column;
		}
	}
</style>


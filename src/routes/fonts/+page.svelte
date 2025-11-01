<script lang="ts">
	const fonts = [
		{ name: 'Bebas Neue', family: 'Bebas Neue', weight: 400, description: 'Bold, condensed, impactful' },
		{ name: 'Oswald', family: 'Oswald', weight: 500, description: 'Strong, modern, geometric' },
		{ name: 'Roboto Condensed', family: 'Roboto Condensed', weight: 700, description: 'Clean, tech-forward' },
		{ name: 'Montserrat', family: 'Montserrat', weight: 600, description: 'Urban, geometric, elegant' },
		{ name: 'Raleway', family: 'Raleway', weight: 600, description: 'Sophisticated, thin lines' },
		{ name: 'Archivo Black', family: 'Archivo Black', weight: 400, description: 'Heavy, powerful, bold' },
		{ name: 'Exo 2', family: 'Exo 2', weight: 600, description: 'Futuristic, technological' },
		{ name: 'Anton', family: 'Anton', weight: 400, description: 'Impact, advertising style' },
		{ name: 'Space Grotesk', family: 'Space Grotesk', weight: 600, description: 'Modern, distinctive' },
		{ name: 'Work Sans', family: 'Work Sans', weight: 600, description: 'Professional, versatile' }
	];
</script>

<svelte:head>
	<title>Font Prototypes - Waterwegregio</title>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Oswald:wght@500&family=Roboto+Condensed:wght@700&family=Montserrat:wght@600&family=Raleway:wght@600&family=Archivo+Black&family=Exo+2:wght@600&family=Anton&family=Space+Grotesk:wght@600&family=Work+Sans:wght@600&display=swap" rel="stylesheet">
</svelte:head>

<div class="prototype-page">
	<header>
		<a href="/" class="back-link">← Terug naar kaart</a>
		<h1>Font Prototypes</h1>
		<p>Klik op je favoriete font om te kiezen</p>
	</header>

	<div class="fonts-grid">
		{#each fonts as font, index}
			<div class="font-card">
				<div class="font-number">{index + 1}</div>
				<div 
					class="font-preview" 
					style="font-family: '{font.family}', sans-serif; font-weight: {font.weight};"
				>
					WATERWEGREGIO VERHALENKAART
				</div>
				<div class="font-info">
					<h3>{font.name}</h3>
					<p>{font.description}</p>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		background: #f9fafb;
		font-family: system-ui, -apple-system, sans-serif;
	}

	.prototype-page {
		min-height: 100vh;
		padding: 40px 20px;
	}

	header {
		max-width: 1200px;
		margin: 0 auto 40px;
		text-align: center;
	}

	.back-link {
		display: inline-block;
		color: #1e5a8e;
		text-decoration: none;
		margin-bottom: 20px;
		font-weight: 500;
		transition: opacity 0.2s;
	}

	.back-link:hover {
		opacity: 0.7;
	}

	header h1 {
		margin: 0 0 10px 0;
		font-size: 32px;
		color: #111827;
	}

	header p {
		margin: 0;
		color: #6b7280;
		font-size: 16px;
	}

	.fonts-grid {
		max-width: 1200px;
		margin: 0 auto;
		display: grid;
		gap: 30px;
	}

	.font-card {
		background: white;
		border-radius: 12px;
		padding: 40px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition: all 0.3s;
		cursor: pointer;
		position: relative;
		border: 3px solid transparent;
	}

	.font-card:hover {
		box-shadow: 0 8px 24px rgba(30, 90, 142, 0.2);
		border-color: #1e5a8e;
		transform: translateY(-2px);
	}

	.font-number {
		position: absolute;
		top: 20px;
		right: 20px;
		background: #1e5a8e;
		color: white;
		width: 36px;
		height: 36px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		font-size: 18px;
	}

	.font-preview {
		font-size: 36px;
		color: #1e5a8e;
		margin-bottom: 20px;
		letter-spacing: 1px;
		text-align: center;
		line-height: 1.2;
		padding: 20px;
		background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
		border-radius: 8px;
		text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.5);
	}

	.font-info {
		text-align: center;
	}

	.font-info h3 {
		margin: 0 0 8px 0;
		font-size: 20px;
		color: #111827;
		font-weight: 600;
	}

	.font-info p {
		margin: 0;
		color: #6b7280;
		font-size: 14px;
		font-style: italic;
	}

	@media (max-width: 768px) {
		.prototype-page {
			padding: 20px 10px;
		}

		.font-preview {
			font-size: 24px;
			padding: 15px;
		}

		.font-card {
			padding: 30px 20px;
		}

		header h1 {
			font-size: 24px;
		}
	}
</style>


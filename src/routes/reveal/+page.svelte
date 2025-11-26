<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { cubicOut, elasticOut } from 'svelte/easing';

	let stage: 'waiting' | 'countdown' | 'opening' | 'revealed' = 'waiting';
	let countdown = 5;
	let confettiPieces: Array<{id: number, x: number, delay: number, duration: number, color: string, size: number, rotation: number}> = [];
	let showTitle = false;
	let curtainProgress = 0;

	const colors = ['#1e5a8e', '#dc2626', '#fbbf24', '#059669', '#7c3aed', '#ec4899', '#06b6d4', '#f97316'];

	function startReveal() {
		stage = 'countdown';
		runCountdown();
	}

	function runCountdown() {
		if (countdown > 0) {
			setTimeout(() => {
				countdown--;
				if (countdown > 0) {
					runCountdown();
				} else {
					openCurtains();
				}
			}, 1000);
		}
	}

	function openCurtains() {
		stage = 'opening';
		
		// Animate curtain progress
		const duration = 2000;
		const start = Date.now();
		
		function animate() {
			const elapsed = Date.now() - start;
			curtainProgress = Math.min(elapsed / duration, 1);
			
			if (curtainProgress < 1) {
				requestAnimationFrame(animate);
			} else {
				stage = 'revealed';
				showTitle = true;
				launchConfetti();
			}
		}
		
		requestAnimationFrame(animate);
	}

	function reset() {
		stage = 'waiting';
		countdown = 5;
		confettiPieces = [];
		showTitle = false;
		curtainProgress = 0;
	}

	onMount(() => {
		// Preload the map iframe
	});
</script>

<svelte:head>
	<title>🎉 Onthulling - Waterwegregio Verhalenkaart</title>
	<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
</svelte:head>

<div class="reveal-container">
	<!-- Background Map (always present, hidden by curtains) -->
	<div class="map-background">
		<iframe 
			src="/" 
			title="Waterwegregio Verhalenkaart"
			class="map-iframe"
		></iframe>
	</div>

	<!-- Confetti -->
	{#each confettiPieces as piece (piece.id)}
		<div 
			class="confetti"
			style="
				left: {piece.x}%;
				animation-delay: {piece.delay}ms;
				animation-duration: {piece.duration}ms;
				background: {piece.color};
				width: {piece.size}px;
				height: {piece.size * 0.6}px;
				transform: rotate({piece.rotation}deg);
			"
		></div>
	{/each}

	<!-- Curtains -->
	{#if stage !== 'revealed'}
		<div class="curtain curtain-left" style="transform: translateX({-curtainProgress * 100}%)">
			<div class="curtain-fabric"></div>
			<div class="curtain-fold"></div>
			<div class="curtain-fold fold-2"></div>
			<div class="curtain-fold fold-3"></div>
		</div>
		<div class="curtain curtain-right" style="transform: translateX({curtainProgress * 100}%)">
			<div class="curtain-fabric"></div>
			<div class="curtain-fold"></div>
			<div class="curtain-fold fold-2"></div>
			<div class="curtain-fold fold-3"></div>
		</div>
		
		<!-- Curtain Rod -->
		<div class="curtain-rod"></div>
		<div class="curtain-rod-end left"></div>
		<div class="curtain-rod-end right"></div>
	{/if}

	<!-- Pre-reveal Content -->
	{#if stage === 'waiting'}
		<div class="waiting-content" transition:fade>
			<div class="logo-container">
				<img src="/monster-logo.png" alt="Monster" class="monster-logo" />
			</div>
			<h1 class="pre-title">Waterwegregio</h1>
			<h2 class="pre-subtitle">Verhalenkaart</h2>
			<p class="pre-description">Een platform voor verhalen uit de regio</p>
			
			<button class="reveal-button" on:click={startReveal}>
				<span class="button-text">🎭 Onthul de Kaart</span>
				<span class="button-glow"></span>
			</button>
			
			<div class="regio-logo">
				<img src="/wwr-logo.jpeg" alt="Regiodeal Waterwegregio" />
			</div>
		</div>
	{/if}

	<!-- Countdown -->
	{#if stage === 'countdown'}
		<div class="countdown-container">
			{#key countdown}
				<div class="countdown-number" in:scale={{duration: 400, easing: elasticOut}} out:fade={{duration: 200}}>
					{countdown}
				</div>
			{/key}
			<div class="countdown-ring"></div>
		</div>
	{/if}

	<!-- Revealed Title -->
	{#if showTitle}
		<div class="revealed-title" transition:fly={{y: -100, duration: 1000, easing: cubicOut}}>
			<div class="title-banner">
				<span class="sparkle">✨</span>
				<h1>De Verhalenkaart is Live!</h1>
				<span class="sparkle">✨</span>
			</div>
		</div>

		<div class="action-buttons" transition:fly={{y: 50, duration: 800, delay: 500}}>
			<a href="/" class="go-to-map">🗺️ Bekijk de Kaart</a>
			<button class="replay-button" on:click={reset}>🔄 Opnieuw</button>
		</div>
	{/if}

	<!-- Sparkles during opening -->
	{#if stage === 'opening'}
		{#each Array(20) as _, i}
			<div 
				class="sparkle-burst"
				style="
					left: 50%;
					top: 50%;
					animation-delay: {i * 50}ms;
					--angle: {(i / 20) * 360}deg;
				"
			>⭐</div>
		{/each}
	{/if}
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		overflow: hidden;
	}

	.reveal-container {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		overflow: hidden;
		background: #0a0a1a;
	}

	/* Map Background */
	.map-background {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 1;
	}

	.map-iframe {
		width: 100%;
		height: 100%;
		border: none;
	}

	/* Curtains */
	.curtain {
		position: absolute;
		top: 0;
		width: 52%;
		height: 100%;
		z-index: 10;
		overflow: hidden;
	}

	.curtain-left {
		left: 0;
	}

	.curtain-right {
		right: 0;
	}

	.curtain-fabric {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background: linear-gradient(
			135deg,
			#8B0000 0%,
			#a51c1c 20%,
			#6d0000 40%,
			#8B0000 60%,
			#a51c1c 80%,
			#6d0000 100%
		);
		box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.5);
	}

	.curtain-fold {
		position: absolute;
		top: 0;
		width: 30%;
		height: 100%;
		background: linear-gradient(
			90deg,
			transparent 0%,
			rgba(0, 0, 0, 0.3) 50%,
			transparent 100%
		);
	}

	.curtain-left .curtain-fold {
		right: 10%;
	}

	.curtain-right .curtain-fold {
		left: 10%;
	}

	.curtain-fold.fold-2 {
		width: 20%;
	}

	.curtain-left .curtain-fold.fold-2 {
		right: 40%;
	}

	.curtain-right .curtain-fold.fold-2 {
		left: 40%;
	}

	.curtain-fold.fold-3 {
		width: 15%;
	}

	.curtain-left .curtain-fold.fold-3 {
		right: 70%;
	}

	.curtain-right .curtain-fold.fold-3 {
		left: 70%;
	}

	/* Curtain Rod */
	.curtain-rod {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 30px;
		background: linear-gradient(180deg, #d4af37 0%, #996515 50%, #d4af37 100%);
		z-index: 20;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
	}

	.curtain-rod-end {
		position: absolute;
		top: -10px;
		width: 50px;
		height: 50px;
		background: radial-gradient(circle at 30% 30%, #f4d03f, #996515);
		border-radius: 50%;
		z-index: 21;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
	}

	.curtain-rod-end.left {
		left: -10px;
	}

	.curtain-rod-end.right {
		right: -10px;
	}

	/* Waiting Content */
	.waiting-content {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 15;
		text-align: center;
		color: white;
	}

	.logo-container {
		margin-bottom: 20px;
	}

	.monster-logo {
		width: 150px;
		height: auto;
		filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
		animation: float 4s ease-in-out infinite, glow 3s ease-in-out infinite alternate;
	}

	@keyframes float {
		0%, 100% { transform: translateY(0) rotate(-2deg); }
		50% { transform: translateY(-20px) rotate(2deg); }
	}

	@keyframes glow {
		0% { filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.3)); }
		100% { filter: drop-shadow(0 0 25px rgba(124, 58, 237, 0.6)); }
	}

	.pre-title {
		font-family: 'Bebas Neue', sans-serif;
		font-size: 5rem;
		margin: 0;
		letter-spacing: 8px;
		text-shadow: 0 0 40px rgba(30, 90, 142, 0.8), 0 4px 20px rgba(0, 0, 0, 0.5);
		background: linear-gradient(135deg, #ffffff 0%, #a8d4ff 50%, #ffffff 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.pre-subtitle {
		font-family: 'Poppins', sans-serif;
		font-size: 2.5rem;
		margin: -10px 0 20px 0;
		font-weight: 600;
		color: #fbbf24;
		text-shadow: 0 0 30px rgba(251, 191, 36, 0.5);
	}

	.pre-description {
		font-size: 1.2rem;
		opacity: 0.8;
		margin-bottom: 40px;
		font-family: 'Poppins', sans-serif;
	}

	.reveal-button {
		position: relative;
		padding: 20px 50px;
		font-size: 1.5rem;
		font-family: 'Poppins', sans-serif;
		font-weight: 700;
		color: white;
		background: linear-gradient(135deg, #1e5a8e 0%, #7c3aed 100%);
		border: none;
		border-radius: 60px;
		cursor: pointer;
		overflow: hidden;
		transition: transform 0.3s, box-shadow 0.3s;
		box-shadow: 0 8px 30px rgba(30, 90, 142, 0.5);
	}

	.reveal-button:hover {
		transform: scale(1.05);
		box-shadow: 0 12px 40px rgba(124, 58, 237, 0.6);
	}

	.button-text {
		position: relative;
		z-index: 1;
	}

	.button-glow {
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
		animation: shimmer 2s infinite;
	}

	@keyframes shimmer {
		0% { left: -100%; }
		100% { left: 100%; }
	}

	.regio-logo {
		margin-top: 50px;
	}

	.regio-logo img {
		height: 80px;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	/* Countdown */
	.countdown-container {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 15;
	}

	.countdown-number {
		font-family: 'Bebas Neue', sans-serif;
		font-size: 20rem;
		color: white;
		text-shadow: 0 0 60px rgba(251, 191, 36, 0.8), 0 0 120px rgba(220, 38, 38, 0.5);
		line-height: 1;
	}

	.countdown-ring {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 350px;
		height: 350px;
		border: 8px solid rgba(255, 255, 255, 0.2);
		border-top-color: #fbbf24;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		0% { transform: translate(-50%, -50%) rotate(0deg); }
		100% { transform: translate(-50%, -50%) rotate(360deg); }
	}

	/* Confetti */
	.confetti {
		position: absolute;
		top: -20px;
		border-radius: 3px;
		z-index: 100;
		animation: confetti-fall linear forwards;
	}

	@keyframes confetti-fall {
		0% {
			transform: translateY(0) rotate(0deg);
			opacity: 1;
		}
		100% {
			transform: translateY(100vh) rotate(720deg);
			opacity: 0;
		}
	}

	/* Revealed Title */
	.revealed-title {
		position: absolute;
		top: 30px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 50;
	}

	.title-banner {
		display: flex;
		align-items: center;
		gap: 20px;
		background: linear-gradient(135deg, rgba(30, 90, 142, 0.95), rgba(124, 58, 237, 0.95));
		padding: 20px 50px;
		border-radius: 20px;
		box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
		backdrop-filter: blur(10px);
	}

	.title-banner h1 {
		font-family: 'Poppins', sans-serif;
		font-size: 2rem;
		margin: 0;
		color: white;
		font-weight: 700;
	}

	.sparkle {
		font-size: 2rem;
		animation: sparkle-pulse 0.5s ease-in-out infinite alternate;
	}

	@keyframes sparkle-pulse {
		0% { transform: scale(1); opacity: 0.8; }
		100% { transform: scale(1.3); opacity: 1; }
	}

	/* Sparkle Burst */
	.sparkle-burst {
		position: absolute;
		font-size: 2rem;
		z-index: 25;
		animation: burst 0.8s ease-out forwards;
	}

	@keyframes burst {
		0% {
			transform: translate(-50%, -50%) translateX(0) scale(0);
			opacity: 1;
		}
		100% {
			transform: translate(-50%, -50%) translateX(150px) rotate(var(--angle)) scale(1.5);
			opacity: 0;
		}
	}

	/* Action Buttons */
	.action-buttons {
		position: absolute;
		bottom: 40px;
		left: 50%;
		transform: translateX(-50%);
		z-index: 50;
		display: flex;
		gap: 20px;
	}

	.go-to-map {
		padding: 16px 40px;
		font-size: 1.3rem;
		font-family: 'Poppins', sans-serif;
		font-weight: 600;
		color: white;
		background: linear-gradient(135deg, #059669, #10b981);
		border: none;
		border-radius: 50px;
		text-decoration: none;
		box-shadow: 0 6px 25px rgba(5, 150, 105, 0.5);
		transition: transform 0.3s, box-shadow 0.3s;
	}

	.go-to-map:hover {
		transform: scale(1.05);
		box-shadow: 0 8px 35px rgba(16, 185, 129, 0.6);
	}

	.replay-button {
		padding: 16px 30px;
		font-size: 1.3rem;
		font-family: 'Poppins', sans-serif;
		font-weight: 600;
		color: #374151;
		background: white;
		border: none;
		border-radius: 50px;
		cursor: pointer;
		box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
		transition: transform 0.3s;
	}

	.replay-button:hover {
		transform: scale(1.05);
	}

	/* Mobile adjustments */
	@media (max-width: 768px) {
		.pre-title {
			font-size: 3rem;
			letter-spacing: 4px;
		}

		.pre-subtitle {
			font-size: 1.5rem;
		}

		.countdown-number {
			font-size: 12rem;
		}

		.countdown-ring {
			width: 250px;
			height: 250px;
		}

		.title-banner {
			padding: 15px 25px;
		}

		.title-banner h1 {
			font-size: 1.2rem;
		}

		.action-buttons {
			flex-direction: column;
			gap: 15px;
		}

		.reveal-button {
			padding: 15px 35px;
			font-size: 1.2rem;
		}
	}
</style>


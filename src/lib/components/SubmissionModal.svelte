<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { fade, scale } from 'svelte/transition';
	import { storyTypes } from '$lib/supabase';
	import { toastStore } from '$lib/stores/toastStore';

	const dispatch = createEventDispatcher();

	export let isOpen = false;
	export let lat: number | null = null;
	export let lng: number | null = null;

	let text = '';
	let selectedType: string = 'bewoner';
	let organisatie = '';
	let naam = '';
	let link = '';
	let isSubmitting = false;
	let error = '';
	let success = false;
	
	// Character counter state
	$: charCount = text.length;
	$: charPercentage = (charCount / 500) * 100;
	$: charCounterClass = charCount >= 500 ? 'danger' : charCount >= 450 ? 'warning' : 'normal';

	function close() {
		isOpen = false;
		text = '';
		selectedType = 'bewoner';
		organisatie = '';
		naam = '';
		link = '';
		error = '';
		success = false;
		dispatch('close');
	}

	async function handleSubmit() {
		if (!text.trim()) {
			toastStore.show('Vul een verhaal in', 'error');
			return;
		}

		if (text.length > 500) {
			toastStore.show('Verhaal mag maximaal 500 tekens bevatten', 'error');
			return;
		}

		if (lat === null || lng === null) {
			toastStore.show('Geen locatie geselecteerd', 'error');
			return;
		}

		isSubmitting = true;
		error = '';

		try {
			const response = await fetch('/api/submit-story', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					text: text.trim(),
					type: selectedType,
					organisatie: organisatie.trim() || null,
					naam: naam.trim() || null,
					link: link.trim() || null,
					lat,
					lng
				})
			});

			const result = await response.json();

			if (!response.ok) {
				throw new Error(result.error || 'Er is een fout opgetreden');
			}

			success = true;
			toastStore.show('Je verhaal is geplaatst! 🎉', 'success');
			setTimeout(() => {
				dispatch('success');
				close();
			}, 1500);
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Er is een fout opgetreden';
			toastStore.show(errorMessage, 'error');
		} finally {
			isSubmitting = false;
		}
	}
</script>

{#if isOpen}
	<div class="modal-backdrop" on:click={close} role="presentation" in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
		<div class="modal" on:click|stopPropagation role="dialog" aria-modal="true" tabindex="-1" in:scale={{ duration: 200, start: 0.95 }} out:scale={{ duration: 150, start: 0.95 }}>
			<div class="modal-header">
				<h2>Deel je verhaal</h2>
				<button class="close-button" on:click={close} aria-label="Sluiten">&times;</button>
			</div>

			{#if success}
				<div class="success-message">
					<p>✓ Je verhaal is geplaatst!</p>
				</div>
			{:else}
				<form on:submit|preventDefault={handleSubmit}>
					<div class="form-group">
						<label for="story-type">
							Type <span class="required">*</span>
						</label>
						<div class="type-selector">
							{#each Object.entries(storyTypes) as [key, type]}
								<button
									type="button"
									class="type-option"
									class:selected={selectedType === key}
									class:project={key === 'project'}
									on:click={() => selectedType = key}
									disabled={isSubmitting}
								>
									<div class="type-icon-wrapper">
										<img src={type.icon} alt={type.label} class="type-icon-img" />
										{#if key === 'project'}
											<div class="type-icon-gradient"></div>
										{/if}
									</div>
									<span class="type-label">{type.label}</span>
								</button>
							{/each}
						</div>
						<p class="type-description">{storyTypes[selectedType].description}</p>
					</div>

					<div class="form-group">
						<label for="story-text">
							Jouw verhaal <span class="required">*</span>
							<span class="char-count {charCounterClass}">{charCount}/500</span>
						</label>
						<div class="char-progress-bar">
							<div class="char-progress-fill {charCounterClass}" style="width: {Math.min(charPercentage, 100)}%"></div>
						</div>
						<textarea
							id="story-text"
							bind:value={text}
							placeholder="Vertel je verhaal over deze plek..."
							maxlength="500"
							rows="6"
							disabled={isSubmitting}
						/>
					</div>

					<div class="form-group">
						<label for="organisatie">
							Organisatie <span class="optional">(optioneel)</span>
						</label>
						<input
							id="organisatie"
							type="text"
							bind:value={organisatie}
							placeholder="Naam van organisatie of initiatief"
							maxlength="100"
							disabled={isSubmitting}
						/>
					</div>

					<div class="form-group">
						<label for="naam">
							Naam <span class="optional">(optioneel)</span>
						</label>
						<input
							id="naam"
							type="text"
							bind:value={naam}
							placeholder="Jouw naam of contactpersoon"
							maxlength="100"
							disabled={isSubmitting}
						/>
					</div>

					<div class="form-group">
						<label for="link">
							Link <span class="optional">(optioneel)</span>
						</label>
						<input
							id="link"
							type="text"
							bind:value={link}
							placeholder="www.example.nl of https://..."
							maxlength="200"
							disabled={isSubmitting}
						/>
					</div>

					{#if error}
						<div class="error-message">{error}</div>
					{/if}

					<div class="form-actions">
						<button type="button" class="btn btn-secondary" on:click={close} disabled={isSubmitting}>
							Annuleren
						</button>
						<button type="submit" class="btn btn-primary" disabled={isSubmitting || !text.trim()}>
							{#if isSubmitting}
								<span class="spinner"></span>
								<span>Bezig...</span>
							{:else}
								Plaatsen
							{/if}
						</button>
					</div>
				</form>
			{/if}
		</div>
	</div>
{/if}

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		backdrop-filter: blur(2px);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 20px;
	}

	.modal {
		background: white;
		border-radius: 12px;
		max-width: 500px;
		width: 100%;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 24px;
		border-bottom: 1px solid #e5e7eb;
	}

	.modal-header h2 {
		margin: 0;
		font-size: 24px;
		font-weight: 600;
		color: #111827;
	}

	.close-button {
		background: none;
		border: none;
		font-size: 32px;
		cursor: pointer;
		color: #6b7280;
		padding: 0;
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
	}

	.close-button:hover {
		color: #111827;
	}

	form {
		padding: 24px;
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

	.type-selector {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 8px;
		margin-bottom: 8px;
	}

	.type-option {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		padding: 12px 8px;
		border: 2px solid #e5e7eb;
		border-radius: 8px;
		background: white;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 13px;
	}

	.type-option:hover:not(:disabled) {
		border-color: #9ca3af;
		background: #f9fafb;
	}

	.type-option.selected {
		border-color: #1e5a8e;
		background: #eff6ff;
	}

	.type-option.project.selected {
		border-color: #dc2626;
		background: #fef2f2;
	}

	.type-option:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.type-icon-wrapper {
		position: relative;
		width: 40px;
		height: 40px;
		transition: transform 0.2s ease;
	}
	
	.type-icon-img {
		width: auto;
		height: 40px;
		object-fit: contain;
		display: block;
		transition: filter 0.2s ease;
	}
	
	/* Color filters for each type */
	.type-option:not(.project) .type-icon-img[alt="Verhaal Bewoner"] {
		filter: brightness(0) saturate(100%) invert(28%) sepia(65%) saturate(1234%) hue-rotate(186deg) brightness(93%) contrast(88%);
	}
	
	.type-option:not(.project) .type-icon-img[alt="Lokaal Initiatief"] {
		filter: brightness(0) saturate(100%) invert(38%) sepia(71%) saturate(1234%) hue-rotate(130deg) brightness(95%) contrast(96%);
	}
	
	.type-option:not(.project) .type-icon-img[alt="Vraag of Behoefte"] {
		filter: brightness(0) saturate(100%) invert(42%) sepia(95%) saturate(2413%) hue-rotate(1deg) brightness(99%) contrast(93%);
	}
	
	.type-option:not(.project) .type-icon-img[alt="Idee"] {
		filter: brightness(0) saturate(100%) invert(35%) sepia(93%) saturate(2718%) hue-rotate(249deg) brightness(93%) contrast(93%);
	}
	
	/* Gradient overlay for project puzzle piece */
	.type-icon-gradient {
		position: absolute;
		top: 0;
		left: 0;
		width: 40px;
		height: 40px;
		background: linear-gradient(135deg, 
			#1e5a8e 0%, 
			#dc2626 25%, 
			#fbbf24 50%, 
			#059669 75%, 
			#7c3aed 100%);
		mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
		-webkit-mask: url('/icons/projectpuzzelstuk.PNG') center/contain no-repeat;
		pointer-events: none;
	}
	
	.type-option.project .type-icon-img {
		opacity: 0;
	}
	
	.type-option:hover .type-icon-wrapper {
		transform: scale(1.1);
	}

	.type-label {
		font-weight: 500;
		text-align: center;
		line-height: 1.2;
	}

	.type-description {
		margin: 0;
		font-size: 12px;
		color: #6b7280;
		font-style: italic;
	}

	.required {
		color: #dc2626;
	}

	.optional {
		color: #9ca3af;
		font-weight: 400;
		font-size: 12px;
	}

	.char-count {
		float: right;
		font-size: 12px;
		font-weight: 500;
		transition: color 0.3s ease;
	}
	
	.char-count.normal {
		color: #059669;
	}
	
	.char-count.warning {
		color: #ea580c;
	}
	
	.char-count.danger {
		color: #dc2626;
		font-weight: 600;
	}
	
	.char-progress-bar {
		height: 3px;
		background: #e5e7eb;
		border-radius: 2px;
		overflow: hidden;
		margin-bottom: 8px;
	}
	
	.char-progress-fill {
		height: 100%;
		transition: width 0.3s ease, background-color 0.3s ease;
		border-radius: 2px;
	}
	
	.char-progress-fill.normal {
		background: linear-gradient(90deg, #059669, #10b981);
	}
	
	.char-progress-fill.warning {
		background: linear-gradient(90deg, #ea580c, #f59e0b);
	}
	
	.char-progress-fill.danger {
		background: linear-gradient(90deg, #dc2626, #ef4444);
	}

	input[type="text"],
	textarea {
		width: 100%;
		padding: 12px;
		border: 1px solid #d1d5db;
		border-radius: 8px;
		font-size: 14px;
		font-family: inherit;
		box-sizing: border-box;
	}

	textarea {
		resize: vertical;
		min-height: 100px;
	}

	input[type="text"]:focus,
	textarea:focus {
		outline: none;
		border-color: #1e5a8e;
		box-shadow: 0 0 0 3px rgba(30, 90, 142, 0.1);
	}

	textarea:disabled {
		background: #f9fafb;
		cursor: not-allowed;
	}

	.form-actions {
		display: flex;
		gap: 12px;
		justify-content: flex-end;
		margin-top: 24px;
	}

	.btn {
		padding: 10px 20px;
		border: none;
		border-radius: 8px;
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-primary {
		background: #1e5a8e;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: #164370;
	}

	.btn-secondary {
		background: #e5e7eb;
		color: #374151;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #d1d5db;
	}

	.error-message {
		padding: 12px;
		background: #fee2e2;
		border: 1px solid #fecaca;
		border-radius: 8px;
		color: #dc2626;
		font-size: 14px;
		margin-top: 16px;
	}

	.success-message {
		padding: 40px 24px;
		text-align: center;
	}

	.success-message p {
		font-size: 20px;
		color: #059669;
		margin: 0;
		font-weight: 500;
	}

	@media (max-width: 640px) {
		.modal {
			margin: 0;
			border-radius: 12px 12px 0 0;
			max-height: 80vh;
		}

		.modal-backdrop {
			align-items: flex-end;
			padding: 0;
		}
	}
</style>


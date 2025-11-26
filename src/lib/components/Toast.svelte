<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	export let message: string = '';
	export let type: 'success' | 'error' | 'info' = 'info';
	export let duration: number = 3000;
	export let onClose: () => void;

	let visible = true;

	// Auto-dismiss after duration
	if (duration > 0) {
		setTimeout(() => {
			visible = false;
			setTimeout(onClose, 300);
		}, duration);
	}

	function handleClose() {
		visible = false;
		setTimeout(onClose, 300);
	}

	const icons = {
		success: '✓',
		error: '✕',
		info: 'ℹ'
	};
</script>

{#if visible}
	<div
		class="toast toast-{type}"
		in:fly={{ y: 50, duration: 300, easing: quintOut }}
		out:fade={{ duration: 200 }}
		role="alert"
	>
		<div class="toast-icon">{icons[type]}</div>
		<p class="toast-message">{message}</p>
		<button class="toast-close" on:click={handleClose} aria-label="Sluiten">
			×
		</button>
	</div>
{/if}

<style>
	.toast {
		position: fixed;
		bottom: 24px;
		right: 24px;
		max-width: 400px;
		min-width: 300px;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 16px;
		border-radius: 12px;
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
		z-index: 10000;
		backdrop-filter: blur(8px);
	}

	.toast-success {
		background: linear-gradient(135deg, rgba(5, 150, 105, 0.95), rgba(16, 185, 129, 0.95));
		color: white;
	}

	.toast-error {
		background: linear-gradient(135deg, rgba(220, 38, 38, 0.95), rgba(239, 68, 68, 0.95));
		color: white;
	}

	.toast-info {
		background: linear-gradient(135deg, rgba(30, 90, 142, 0.95), rgba(59, 130, 246, 0.95));
		color: white;
	}

	.toast-icon {
		flex-shrink: 0;
		width: 28px;
		height: 28px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
		font-weight: 700;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
	}

	.toast-message {
		margin: 0;
		flex: 1;
		font-size: 14px;
		font-weight: 500;
		line-height: 1.4;
	}

	.toast-close {
		flex-shrink: 0;
		background: none;
		border: none;
		color: white;
		font-size: 24px;
		cursor: pointer;
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 4px;
		padding: 0;
		opacity: 0.7;
		transition: opacity 0.2s ease, background 0.2s ease;
	}

	.toast-close:hover {
		opacity: 1;
		background: rgba(255, 255, 255, 0.1);
	}

	@media (max-width: 768px) {
		.toast {
			bottom: 16px;
			right: 16px;
			left: 16px;
			max-width: none;
			min-width: 0;
		}
	}
</style>


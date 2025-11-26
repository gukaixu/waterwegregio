import { writable } from 'svelte/store';

export interface Toast {
	id: string;
	message: string;
	type: 'success' | 'error' | 'info';
	duration?: number;
}

function createToastStore() {
	const { subscribe, update } = writable<Toast[]>([]);

	return {
		subscribe,
		show: (message: string, type: 'success' | 'error' | 'info' = 'info', duration = 3000) => {
			const id = `toast-${Date.now()}-${Math.random()}`;
			const toast: Toast = { id, message, type, duration };
			
			update(toasts => [...toasts, toast]);
		},
		remove: (id: string) => {
			update(toasts => toasts.filter(t => t.id !== id));
		}
	};
}

export const toastStore = createToastStore();


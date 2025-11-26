import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const ADMIN_PASSWORD = 'resilientdelta2025';

function createAdminStore() {
	// Initialize from sessionStorage if in browser
	const initialValue = browser ? sessionStorage.getItem('admin_auth') === 'true' : false;
	const { subscribe, set, update } = writable<boolean>(initialValue);

	return {
		subscribe,
		login: (password: string): boolean => {
			if (password === ADMIN_PASSWORD) {
				set(true);
				if (browser) {
					sessionStorage.setItem('admin_auth', 'true');
				}
				return true;
			}
			return false;
		},
		logout: () => {
			set(false);
			if (browser) {
				sessionStorage.removeItem('admin_auth');
			}
		},
		// For checking password without storing
		checkPassword: (password: string): boolean => {
			return password === ADMIN_PASSWORD;
		}
	};
}

export const adminStore = createAdminStore();


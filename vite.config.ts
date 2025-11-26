import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	build: {
		sourcemap: false // Disable sourcemaps in production for smaller builds
	},
	server: {
		fs: {
			strict: true
		}
	}
});

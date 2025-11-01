import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL } from '$env/static/public';
import { SUPABASE_SERVICE_ROLE_KEY } from '$env/static/private';

export const DELETE: RequestHandler = async ({ request }) => {
	try {
		const { id } = await request.json();

		// Validate input
		if (!id || typeof id !== 'string') {
			return json({ error: 'Story ID is verplicht' }, { status: 400 });
		}

		// Create Supabase client with service role key (bypasses RLS)
		const supabase = createClient(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

		// Delete story from database
		const { error } = await supabase.from('stories').delete().eq('id', id);

		if (error) {
			console.error('Supabase error:', error);
			return json({ error: 'Fout bij verwijderen verhaal' }, { status: 500 });
		}

		return json({ success: true });
	} catch (error) {
		console.error('Error deleting story:', error);
		return json({ error: 'Er is een onverwachte fout opgetreden' }, { status: 500 });
	}
};


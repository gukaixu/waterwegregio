import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL } from '$env/static/public';
import { SUPABASE_SERVICE_ROLE_KEY } from '$env/static/private';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { text, type, organisatie, naam, link, lat, lng } = await request.json();

		// Validate input
		if (!text || typeof text !== 'string' || text.trim().length === 0) {
			return json({ error: 'Verhaal is verplicht' }, { status: 400 });
		}

		if (text.length > 500) {
			return json({ error: 'Verhaal mag maximaal 500 tekens bevatten' }, { status: 400 });
		}

		if (typeof lat !== 'number' || typeof lng !== 'number') {
			return json({ error: 'Ongeldige locatie' }, { status: 400 });
		}

		// Validate latitude and longitude ranges
		if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
			return json({ error: 'Locatie buiten bereik' }, { status: 400 });
		}

		// Create Supabase client with service role key (bypasses RLS)
		const supabase = createClient(PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

		// Validate type
		const validTypes = ['project', 'bewoner', 'initiatief', 'vraag', 'idee'];
		if (!type || !validTypes.includes(type)) {
			return json({ error: 'Ongeldig type' }, { status: 400 });
		}

		// Validate optional fields
		if (organisatie && organisatie.length > 100) {
			return json({ error: 'Organisatie naam te lang (max 100 tekens)' }, { status: 400 });
		}

		if (naam && naam.length > 100) {
			return json({ error: 'Naam te lang (max 100 tekens)' }, { status: 400 });
		}

		if (link && link.length > 200) {
			return json({ error: 'Link te lang (max 200 tekens)' }, { status: 400 });
		}

		// Basic URL validation (allow www. format)
		if (link && link.trim()) {
			const urlPattern = /^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;
			if (!urlPattern.test(link.trim())) {
				return json({ error: 'Ongeldig link formaat' }, { status: 400 });
			}
		}

		// Insert story into database
		// PostGIS expects POINT(lng lat) format
		const { data, error } = await supabase
			.from('stories')
			.insert({
				location: `POINT(${lng} ${lat})`,
				text: text.trim(),
				type: type,
				organisatie: organisatie?.trim() || null,
				naam: naam?.trim() || null,
				link: link?.trim() || null,
				language: 'nl',
				status: 'approved' // Auto-approve for MVP
			})
			.select()
			.single();

		if (error) {
			console.error('Supabase error:', error);
			return json({ error: 'Fout bij opslaan verhaal' }, { status: 500 });
		}

		return json({ success: true, story: data });
	} catch (error) {
		console.error('Error submitting story:', error);
		return json({ error: 'Er is een onverwachte fout opgetreden' }, { status: 500 });
	}
};


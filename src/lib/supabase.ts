import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

// Create Supabase client for browser use
export const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);

// Types for our database
export interface Story {
	id: string;
	location: string; // PostGIS geography stored as WKT
	text: string;
	type: 'project' | 'bewoner' | 'initiatief' | 'vraag' | 'idee';
	organisatie?: string;
	naam?: string;
	link?: string;
	language: string;
	status: 'pending' | 'approved' | 'rejected';
	created_at: string;
	updated_at: string;
}

export interface StoryWithCoords {
	id: string;
	lat: number;
	lng: number;
	text: string;
	type: 'project' | 'bewoner' | 'initiatief' | 'vraag' | 'idee';
	organisatie?: string;
	naam?: string;
	link?: string;
	language: string;
	status: 'pending' | 'approved' | 'rejected';
	created_at: string;
	updated_at: string;
}

export const storyTypes = {
	project: {
		label: 'Regiodeal Project',
		icon: '🎯',
		color: '#dc2626', // Red - stands out
		description: 'Officieel Regiodeal Waterwegregio project'
	},
	bewoner: {
		label: 'Verhaal Bewoner',
		icon: '💬',
		color: '#1e5a8e', // Blue
		description: 'Persoonlijk verhaal of ervaring van een bewoner'
	},
	initiatief: {
		label: 'Lokaal Initiatief',
		icon: '🌟',
		color: '#059669', // Green
		description: 'Burgerinitiatief of lokaal project'
	},
	vraag: {
		label: 'Vraag of Behoefte',
		icon: '❓',
		color: '#ea580c', // Orange
		description: 'Vraag, wens of behoefte uit de buurt'
	},
	idee: {
		label: 'Idee',
		icon: '💡',
		color: '#7c3aed', // Purple
		description: 'Nieuw idee of voorstel voor de regio'
	}
};


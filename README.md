# Waterwegregio Verhalen Kaart

Een crowdsourcing kaart waar gebruikers anoniem verhalen kunnen delen over locaties in de Waterwegregio. Geïnspireerd door Queering the Map.

## 📋 Overzicht

Dit project is gebouwd met:
- **SvelteKit** - Modern web framework
- **Supabase** - PostgreSQL database met PostGIS voor geografische data
- **MapLibre GL** - Open-source kaart rendering
- **Cloudflare Turnstile** - CAPTCHA voor spam-bescherming
- **Vercel** - Hosting platform

## 🏗️ Architectuur

- **Frontend**: SvelteKit app met MapLibre GL voor kaartweergave
- **Backend**: Supabase (PostgreSQL + PostGIS + Row Level Security)
- **Authenticatie**: Cloudflare Turnstile voor anonieme submissions
- **Moderatie**: Admin panel (geprepareerd, auto-approve voor MVP)

## 🚀 Setup Instructies

### 1. Supabase Project Opzetten

#### A. Create Supabase Project

1. Ga naar [supabase.com](https://supabase.com) en maak een gratis account
2. Klik op "New Project"
3. Vul project details in:
   - **Name**: `waterwegregio-stories`
   - **Database Password**: Kies een sterk wachtwoord (sla op in wachtwoord manager)
   - **Region**: Europe (Frankfurt) of dichtsbijzijnde regio
4. Klik "Create new project" en wacht ~2 minuten

#### B. Enable PostGIS Extension

1. Ga naar SQL Editor in je Supabase dashboard
2. Maak een nieuwe query en voer uit:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

#### C. Run Database Migration

1. Kopieer de inhoud van `supabase/migrations/001_create_stories.sql`
2. Plak in SQL Editor en voer uit
3. Controleer dat de `stories` tabel is aangemaakt onder "Table Editor"

#### D. Get API Keys

1. Ga naar Settings → API
2. Kopieer de volgende waarden:
   - **Project URL** (bijv. `https://abcdefgh.supabase.co`)
   - **anon public** key (lang token)
   - **service_role** key (secret, alleen server-side gebruiken)

### 2. Cloudflare Turnstile Opzetten

1. Ga naar [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigeer naar "Turnstile" in het menu
3. Klik "Add Site"
4. Configureer:
   - **Site name**: `Waterwegregio Verhalen`
   - **Domain**: Jouw domein of `localhost` voor development
   - **Widget Mode**: Managed (aanbevolen)
5. Klik "Create"
6. Kopieer:
   - **Site Key** (public)
   - **Secret Key** (private)

### 3. Environment Variables Instellen

Kopieer `.env.example` naar `.env.local`:

```bash
cp .env.example .env.local
```

Vul de waarden in:

```env
# Supabase Configuration
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Cloudflare Turnstile (CAPTCHA)
PUBLIC_CLOUDFLARE_TURNSTILE_SITE_KEY=your-site-key-here
CLOUDFLARE_TURNSTILE_SECRET=your-secret-key-here

# Admin Panel (optioneel - default is "waterweg2025")
ADMIN_PASSWORD_HASH=waterweg2025
```

### 4. Dependencies Installeren

```bash
npm install
```

### 5. Lokale Development

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in je browser.

#### Test Flows

1. **Story toevoegen**:
   - Klik op de kaart binnen Waterwegregio grenzen
   - Vul een verhaal in
   - Voltooi CAPTCHA
   - Submit

2. **Admin panel**:
   - Ga naar [http://localhost:5173/admin](http://localhost:5173/admin)
   - Wachtwoord: `waterweg2025`
   - Bekijk, goedkeuren, of verwijder verhalen

## 🌍 Deployment naar Vercel

### Optie 1: Via Vercel Dashboard (Aanbevolen)

1. Push je code naar GitHub
2. Ga naar [vercel.com](https://vercel.com)
3. Klik "New Project"
4. Import je GitHub repository
5. Configureer:
   - **Framework Preset**: SvelteKit (auto-detected)
   - **Root Directory**: `web` (of `.` als dit de root is)
6. Voeg Environment Variables toe (kopieer uit `.env.local`):
   - `PUBLIC_SUPABASE_URL`
   - `PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `PUBLIC_CLOUDFLARE_TURNSTILE_SITE_KEY`
   - `CLOUDFLARE_TURNSTILE_SECRET`
7. Klik "Deploy"

### Optie 2: Via Vercel CLI

```bash
npm i -g vercel
vercel login
vercel --prod
```

Volg de prompts en voeg environment variables toe via dashboard.

### Custom Domain (Optioneel)

1. Ga naar je project in Vercel dashboard
2. Settings → Domains
3. Voeg jouw domein toe (bijv. `verhalen.waterwegregio.nl`)
4. Configureer DNS volgens Vercel instructies
5. Update Cloudflare Turnstile domein whitelist

## 💰 Kosten Overzicht

### MVP / Pilot (tot ~1000 verhalen, ~5000 bezoekers/maand)

| Service | Tier | Maandelijkse Kosten |
|---------|------|---------------------|
| Supabase | Free | €0 |
| Vercel | Hobby | €0 |
| Cloudflare Turnstile | Free | €0 |
| **Totaal** | | **€0** |

#### Supabase Free Tier Limieten:
- 500 MB database (genoeg voor ~250k verhalen)
- 1 GB file storage
- 5 GB egress bandwidth
- 2 projecten

#### Vercel Hobby Limieten:
- 100 GB bandwidth
- Commercial use niet officieel toegestaan (academisch project = OK)

### Production (bij groei)

| Service | Tier | Maandelijkse Kosten |
|---------|------|---------------------|
| Supabase | Pro | $25 (~€24) |
| Vercel | Pro | $20 (~€19) |
| Cloudflare Turnstile | Free | €0 |
| **Totaal** | | **~€43** |

#### Wanneer upgraden?

**Supabase Pro**: Wanneer je:
- Meer dan 500 MB data hebt
- Geen pausing wilt (Free projects slapen na 1 week inactiviteit)
- Dagelijkse backups wilt
- Email support nodig hebt

**Vercel Pro**: Wanneer je:
- Meer dan 100 GB bandwidth gebruikt
- Commercial/official university branding wilt
- Team collaboration nodig hebt

## 🔒 Beveiliging & Moderatie

### Row Level Security (RLS)

Supabase RLS policies beschermen de database:

- **Insert**: Iedereen kan verhalen plaatsen (met CAPTCHA verificatie)
- **Select**: Alleen goedgekeurde verhalen zijn publiek zichtbaar
- **Update/Delete**: Alleen via service role key (admin panel)

### Moderatie Workflow

**Huidige setup (MVP)**: Auto-approve
- Alle nieuwe verhalen krijgen status `approved`
- Direct zichtbaar op de kaart
- Achteraf modereren via admin panel

**Toekomstige setup**: Pre-moderation
1. Wijzig in `src/routes/api/submit-story/+server.ts`:
   ```typescript
   status: 'pending' // was: 'approved'
   ```
2. Nieuwe verhalen worden niet getoond totdat admin goedkeurt
3. Admin krijgt notification (add email notification service)

### CAPTCHA Bescherming

Cloudflare Turnstile voorkomt:
- Geautomatiseerde spam
- Bot attacks
- Mass submissions

Rate limiting gebeurt automatisch via Turnstile.

## 📱 Features

### Gebruikers Features
- 🗺️ Interactieve kaart met Waterwegregio grenzen
- 📍 Klik-om-pin-te-plaatsen interface
- ✍️ Anonieme verhalen delen (max 500 tekens)
- 🤖 CAPTCHA bescherming tegen spam
- 📱 Volledig responsive (mobiel-vriendelijk)
- 🔍 Clustering voor dichte pin-groepen
- 💬 Popup met verhaal bij klik op pin

### Admin Features
- 🔐 Wachtwoord-beschermde toegang
- 📊 Overzicht van alle verhalen
- ✅ Goedkeuren/afwijzen functionaliteit
- 🗑️ Verhalen verwijderen
- 🔍 Filter op status (pending/approved/rejected)
- 📍 Locatie coördinaten per verhaal

## 🛠️ Development Tips

### Lokale Supabase (Optioneel)

Voor offline development:

```bash
# Install Supabase CLI
npm install -g supabase

# Start local Supabase
supabase start

# Run migrations
supabase db push

# Get local connection string
supabase status
```

Update `.env.local` met lokale credentials.

### Database Queries Testen

Via Supabase SQL Editor of lokaal:

```sql
-- Alle verhalen ophalen
SELECT id, ST_AsText(location::geometry) as coords, text, status, created_at 
FROM stories 
ORDER BY created_at DESC;

-- Verhalen binnen bounding box
SELECT * FROM stories 
WHERE ST_DWithin(
  location::geography,
  ST_MakePoint(4.4, 51.9)::geography,
  10000  -- 10km radius
);

-- Aantal per status
SELECT status, COUNT(*) 
FROM stories 
GROUP BY status;
```

### TypeScript Types Genereren

Supabase CLI kan TypeScript types genereren:

```bash
supabase gen types typescript --project-id your-project-ref > src/lib/database.types.ts
```

## 📝 Data Model

### `stories` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `location` | GEOGRAPHY(POINT) | PostGIS point (lng, lat) |
| `text` | TEXT | Verhaal content (max 500 chars) |
| `language` | VARCHAR(10) | Taal code (default: 'nl') |
| `status` | VARCHAR(20) | 'pending', 'approved', of 'rejected' |
| `created_at` | TIMESTAMPTZ | Aanmaak timestamp |
| `updated_at` | TIMESTAMPTZ | Update timestamp (auto) |

### Indexes

- `idx_stories_location` - GIST index voor spatial queries
- `idx_stories_status` - B-tree voor status filtering
- `idx_stories_created_at` - B-tree voor chronologische sorting

## 🧪 Testing

```bash
# Type checking
npm run check

# Build production
npm run build

# Preview production build
npm run preview
```

## 🆘 Troubleshooting

### "Failed to fetch stories"
- Check Supabase URL en anon key in `.env.local`
- Verify PostGIS extension is enabled
- Check RLS policies zijn correct

### "Turnstile verification failed"
- Verify site key en secret key
- Check domein whitelist in Cloudflare
- Test met `localhost` toegevoegd aan allowed domains

### Map niet zichtbaar
- Check MapLibre CSS is geïmporteerd in `+page.svelte`
- Verify `waterwegregio_boundary.geojson` bestaat in `static/data/`
- Check browser console voor errors

### Admin login werkt niet
- Default wachtwoord is `waterweg2025`
- Check sessionStorage in browser DevTools
- Try incognito mode om cache issues uit te sluiten

## 📚 Resources

- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [Supabase Docs](https://supabase.com/docs)
- [MapLibre GL Docs](https://maplibre.org/maplibre-gl-js/docs/)
- [PostGIS Reference](https://postgis.net/docs/)
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/)

## 🤝 Contributing

Voor bugs of feature requests:
1. Check bestaande issues
2. Maak nieuwe issue met duidelijke beschrijving
3. Voor PRs: fork, branch, commit, PR

## 📄 License

Dit project is ontwikkeld voor Waterwegregio | Erasmus Universiteit Rotterdam.

---

**Contact**: Voor vragen over setup of deployment, neem contact op met het projectteam.

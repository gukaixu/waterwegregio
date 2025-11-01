# Quick Start Guide

Snel aan de slag met de Waterwegregio Verhalen Kaart in 5 minuten.

## 📋 Voordat je begint

Je hebt nodig:
- Node.js 18+ geïnstalleerd
- Een Supabase account (gratis)
- Een Cloudflare account (gratis)

## ⚡ 5-Minuten Setup

### 1. Supabase Setup (2 min)

1. Ga naar [supabase.com](https://supabase.com) → Create new project
2. Kies naam `waterwegregio-stories` en wacht op provisioning
3. Ga naar SQL Editor → New query
4. Kopieer en voer uit: `CREATE EXTENSION IF NOT EXISTS postgis;`
5. Kopieer inhoud van `supabase/migrations/001_create_stories.sql` → Execute
6. Ga naar Settings → API → Kopieer URL + anon key + service_role key

### 2. Cloudflare Turnstile (1 min)

1. Ga naar [dash.cloudflare.com](https://dash.cloudflare.com) → Turnstile
2. Add site: naam "Waterwegregio", domain "localhost"
3. Kopieer Site Key + Secret Key

### 3. Lokaal Starten (2 min)

```bash
# Environment variables instellen
cp .env.example .env.local
# Open .env.local en vul je keys in

# Dependencies installeren
npm install

# Ontwikkelserver starten
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## ✅ Test Checklist

- [ ] Kaart laadt met Waterwegregio grenzen
- [ ] Klik op kaart → modal opent
- [ ] Vul verhaal in + CAPTCHA → submit werkt
- [ ] Pin verschijnt op kaart
- [ ] Klik op pin → popup toont verhaal
- [ ] Ga naar `/admin` → login met `waterweg2025`
- [ ] Zie je verhaal in admin panel

## 🚀 Deploy naar Vercel

```bash
# Push naar GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main

# Dan in Vercel dashboard:
# 1. Import GitHub repo
# 2. Add environment variables uit .env.local
# 3. Deploy
```

Klaar! 🎉

## 📚 Volgende Stappen

- Lees [README.md](./README.md) voor uitgebreide documentatie
- Pas admin wachtwoord aan in `src/routes/admin/+page.svelte`
- Overweeg pre-moderation (zie README → Moderatie Workflow)
- Configureer custom domain in Vercel

## 🆘 Hulp Nodig?

- Kaart laadt niet? → Check `.env.local` keys
- CAPTCHA werkt niet? → Voeg `localhost` toe aan Cloudflare domains
- Database errors? → Verify PostGIS extension is enabled
- Admin login werkt niet? → Default wachtwoord is `waterweg2025`

**Meer info**: Zie [README.md](./README.md) of neem contact op met het team.


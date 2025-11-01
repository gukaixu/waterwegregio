# Deployment Guide - Waterwegregio Verhalen Kaart

## Quick Deploy to Vercel (Recommended)

### Prerequisites
- [Vercel account](https://vercel.com/signup) (free)
- GitHub repository (or use Vercel CLI)
- Supabase project credentials

---

## Option 1: Deploy via GitHub (Easiest)

### Step 1: Push to GitHub

```bash
cd /Users/kees/Library/CloudStorage/OneDrive-ErasmusUniversityRotterdam/EUR/waterwegregio/web

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - Waterwegregio Verhalen Kaart"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/waterwegregio-verhalen.git
git branch -M main
git push -u origin main
```

### Step 2: Connect to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. **Import** your GitHub repository
4. Vercel will auto-detect SvelteKit ✅
5. **Configure Environment Variables** (see below)
6. Click **"Deploy"**

### Step 3: Set Environment Variables in Vercel

In your Vercel project settings → **Environment Variables**, add:

```
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

⚠️ **Important:** Make sure these are set for **Production**, **Preview**, and **Development** environments.

---

## Option 2: Deploy via Vercel CLI

### Install Vercel CLI

```bash
npm i -g vercel
```

### Deploy

```bash
cd /Users/kees/Library/CloudStorage/OneDrive-ErasmusUniversityRotterdam/EUR/waterwegregio/web

# Login to Vercel
vercel login

# Deploy (will prompt for environment variables)
vercel

# For production deployment
vercel --prod
```

---

## Environment Variables Needed

Copy these from your Supabase project dashboard:

### Public Variables
- `PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon/public key

### Private Variables
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key (keep secret!)

### Where to find these in Supabase:
1. Go to [app.supabase.com](https://app.supabase.com)
2. Select your project
3. **Settings** → **API**
4. Copy the values

---

## Post-Deployment Checklist

### ✅ Configure Custom Domain (Optional)
1. In Vercel project settings → **Domains**
2. Add your custom domain (e.g., `verhalen.waterwegregio.nl`)
3. Update DNS records as shown by Vercel

### ✅ Test the Deployment
1. Visit your Vercel URL
2. Try adding a story
3. Check admin panel: `https://your-app.vercel.app/admin`
   - Password: `resilientdelta2025`

### ✅ Database Migrations
Make sure you've run all migrations in Supabase:
- Migration `001_create_stories.sql` ✅
- Migration `003_add_story_type.sql` ✅
- Migration `004_add_optional_fields.sql` ✅

### ✅ Security Review
- [ ] Service role key is only in environment variables (not in code)
- [ ] `.env.local` is in `.gitignore`
- [ ] Admin password is secure
- [ ] Supabase RLS policies are enabled

---

## Alternative Hosting Options

### Netlify
- Also supports SvelteKit
- Change adapter: `npm i -D @sveltejs/adapter-netlify`
- Update `svelte.config.js`

### Cloudflare Pages
- Great CDN performance
- Change adapter: `npm i -D @sveltejs/adapter-cloudflare`
- Update `svelte.config.js`

---

## Troubleshooting

### Build fails on Vercel
- Check that all dependencies are in `package.json`
- Ensure Node version is compatible (Node 18+ recommended)
- Check build logs for specific errors

### Environment variables not working
- Make sure variables are set for the correct environment
- Redeploy after adding new variables
- Check variable names match exactly (case-sensitive)

### Map doesn't load
- Check browser console for errors
- Verify `/static/map-style.json` is accessible
- Check network tab for failed requests

### Stories not appearing
- Verify Supabase connection
- Check database migrations are applied
- Review browser console for API errors

---

## Monitoring & Analytics

### Vercel Analytics
Enable in project settings → **Analytics** (free tier available)

### Error Tracking
Consider adding:
- [Sentry](https://sentry.io) for error tracking
- Vercel's built-in logging

---

## Backup & Maintenance

### Database Backups
- Supabase automatically backs up your database daily
- Download manual backups from Supabase dashboard

### Code Backups
- Keep GitHub repository up to date
- Tag releases: `git tag v1.0.0`

---

## Cost Estimate

### Free Tier Limits:
- **Vercel**: 100 GB bandwidth/month, unlimited requests
- **Supabase**: 500 MB database, 2 GB bandwidth, 50,000 monthly active users

**Expected monthly cost for university project: €0** 🎉

For higher traffic, consider paid tiers starting at:
- Vercel Pro: $20/month
- Supabase Pro: $25/month

---

## Support

- Vercel docs: https://vercel.com/docs/frameworks/sveltekit
- SvelteKit docs: https://kit.svelte.dev/docs
- Supabase docs: https://supabase.com/docs

---

**Good luck with your deployment!** 🚀


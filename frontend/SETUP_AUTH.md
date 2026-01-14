# Quick Setup Guide

## Step 1: Get Supabase Credentials

1. Go to [supabase.com](https://supabase.com) and sign in
2. Create a new project (or use existing)
3. Go to **Settings** → **API**
4. Copy your **Project URL** and **anon public key**

## Step 2: Create .env File

Create a file named `.env` in `d:\BookRecommendation\frontend\` with:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

Replace the values with your actual credentials from Step 1.

## Step 3: Restart Dev Server

After creating the `.env` file:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
npm run dev
```

## Step 4: Test Authentication

1. Open http://localhost:5173
2. Click "Sign In" button
3. Try signing up with a new account
4. Test the sign-in flow

## Optional: Configure Email Settings

In Supabase dashboard:
- Go to **Authentication** → **Providers** → **Email**
- Toggle "Confirm email" based on your preference
- If disabled, users can sign in immediately after registration

---

**That's it!** Your authentication system is ready to use.

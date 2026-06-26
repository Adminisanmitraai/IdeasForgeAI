# Supabase Plan

IdeasForgeAI currently keeps generated app data in local JSON files. KisanMitraLite is prepared for a later Supabase migration without requiring Supabase during local testing.

Planned tables:
- farmers
- fpos
- buyers
- farms
- crops
- mandi_deals
- accounts
- weather_records
- users
- roles

Environment variables:
- SUPABASE_URL=
- SUPABASE_ANON_KEY=
- SUPABASE_SERVICE_ROLE_KEY=

Frontend rule:
- Never place `SUPABASE_SERVICE_ROLE_KEY` in frontend files.
- Public frontend code may use only `SUPABASE_URL` and `SUPABASE_ANON_KEY` after Row Level Security is configured.

-- Run this manually in the Supabase SQL editor or with your preferred migration tool.
-- The frontend only uses VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.

create or replace function public.westgard_set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists public.westgard_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.westgard_flashcard_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  deck_id text not null,
  progress jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (user_id, deck_id),
  constraint westgard_flashcard_progress_object check (jsonb_typeof(progress) = 'object')
);

drop trigger if exists westgard_profiles_set_updated_at on public.westgard_profiles;
create trigger westgard_profiles_set_updated_at
before update on public.westgard_profiles
for each row execute function public.westgard_set_updated_at();

drop trigger if exists westgard_flashcard_progress_set_updated_at on public.westgard_flashcard_progress;
create trigger westgard_flashcard_progress_set_updated_at
before update on public.westgard_flashcard_progress
for each row execute function public.westgard_set_updated_at();

alter table public.westgard_profiles enable row level security;
alter table public.westgard_flashcard_progress enable row level security;

drop policy if exists "westgard_profiles_select_own" on public.westgard_profiles;
create policy "westgard_profiles_select_own"
on public.westgard_profiles
for select
using (id = auth.uid());

drop policy if exists "westgard_profiles_insert_own" on public.westgard_profiles;
create policy "westgard_profiles_insert_own"
on public.westgard_profiles
for insert
with check (id = auth.uid());

drop policy if exists "westgard_profiles_update_own" on public.westgard_profiles;
create policy "westgard_profiles_update_own"
on public.westgard_profiles
for update
using (id = auth.uid())
with check (id = auth.uid());

drop policy if exists "westgard_flashcard_progress_select_own" on public.westgard_flashcard_progress;
create policy "westgard_flashcard_progress_select_own"
on public.westgard_flashcard_progress
for select
using (user_id = auth.uid());

drop policy if exists "westgard_flashcard_progress_insert_own" on public.westgard_flashcard_progress;
create policy "westgard_flashcard_progress_insert_own"
on public.westgard_flashcard_progress
for insert
with check (user_id = auth.uid());

drop policy if exists "westgard_flashcard_progress_update_own" on public.westgard_flashcard_progress;
create policy "westgard_flashcard_progress_update_own"
on public.westgard_flashcard_progress
for update
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "westgard_flashcard_progress_delete_own" on public.westgard_flashcard_progress;
create policy "westgard_flashcard_progress_delete_own"
on public.westgard_flashcard_progress
for delete
using (user_id = auth.uid());

-- Esquema de la sincronización del progreso (RAG & Multi-Agent Academy).
-- Se aplica una vez en el editor SQL de Supabase (SQL Editor > New query > pegar > Run).
-- Es idempotente: se puede volver a ejecutar.

create table if not exists public.progress (
  user_id        uuid primary key references auth.users (id) on delete cascade,
  data           jsonb not null,
  schema_version int not null default 2,
  -- Revisión para la concurrencia optimista: la sube el trigger en cada actualización.
  revision       bigint not null default 1,
  updated_at     timestamptz not null default now(),
  -- Tope de tamaño (≈ 1 MB) para que una cuenta no pueda llenar la base de datos.
  constraint progress_data_size check (pg_column_size(data) < 1000000)
);

alter table public.progress enable row level security;

-- Cada persona autenticada solo ve y modifica SU fila. Sin sesión (rol anon) no hay acceso.
drop policy if exists "progress_select_own" on public.progress;
create policy "progress_select_own" on public.progress
  for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "progress_insert_own" on public.progress;
create policy "progress_insert_own" on public.progress
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

drop policy if exists "progress_update_own" on public.progress;
create policy "progress_update_own" on public.progress
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "progress_delete_own" on public.progress;
create policy "progress_delete_own" on public.progress
  for delete to authenticated
  using ((select auth.uid()) = user_id);

revoke all on public.progress from anon;

-- En cada actualización: sube la revisión, sella la hora y no deja cambiar el propietario.
create or replace function public.progress_touch()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.revision   := old.revision + 1;
  new.updated_at := now();
  new.user_id    := old.user_id;
  return new;
end;
$$;

drop trigger if exists progress_touch on public.progress;
create trigger progress_touch
  before update on public.progress
  for each row execute function public.progress_touch();

-- Comprobación manual de las políticas (en el editor SQL, sustituye los UUID por usuarios reales):
--   begin;
--   set local role authenticated;
--   select set_config('request.jwt.claims', '{"sub":"<UUID_DEL_USUARIO_A>"}', true);
--   select * from public.progress;                 -- solo debe aparecer la fila de A
--   select set_config('request.jwt.claims', '{"sub":"<UUID_DEL_USUARIO_B>"}', true);
--   select * from public.progress;                 -- solo debe aparecer la fila de B
--   rollback;

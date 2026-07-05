-- ============================================================
-- Migration 3: per-referral discussion threads (ticket-style chat)
-- Run once in Supabase SQL Editor, AFTER the first two migrations.
-- ============================================================

create table if not exists public.referral_messages (
  id          uuid primary key default gen_random_uuid(),
  referral_id uuid not null references public.referrals(id) on delete cascade,
  sender      text not null check (sender in ('partner','admin')),
  body        text not null check (length(body) between 1 and 2000),
  created_at  timestamptz not null default now()
);

create index if not exists idx_msgs_referral on public.referral_messages(referral_id, created_at);

-- read markers for unread badges on both sides
alter table public.referrals add column if not exists partner_last_read_at timestamptz not null default now();
alter table public.referrals add column if not exists admin_last_read_at   timestamptz not null default now();

alter table public.referral_messages enable row level security;

drop policy if exists admin_all_messages on public.referral_messages;
create policy admin_all_messages on public.referral_messages
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'raguls09@gmail.com')
  with check ((auth.jwt() ->> 'email') = 'raguls09@gmail.com');

-- ---------- helper: validate partner owns referral ----------
create or replace function public._partner_referral(p_code text, p_referral uuid)
returns uuid
language plpgsql security definer set search_path = public as $$
declare v_rid uuid;
begin
  select r.id into v_rid
  from referrals r
  join partners p on p.id = r.partner_id
  where r.id = p_referral and upper(p.code) = upper(trim(p_code)) and p.active = true;
  return v_rid; -- null if not owned / inactive
end; $$;

revoke all on function public._partner_referral(text, uuid) from public;

-- ---------- read thread (also marks partner as caught up) ----------
create or replace function public.get_referral_messages(p_code text, p_referral uuid)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_rid uuid; v_msgs jsonb;
begin
  v_rid := _partner_referral(p_code, p_referral);
  if v_rid is null then return jsonb_build_object('ok', false); end if;

  update referrals set partner_last_read_at = now() where id = v_rid;

  select coalesce(jsonb_agg(jsonb_build_object(
    'sender', m.sender,
    'body',   m.body,
    'at',     to_char(m.created_at at time zone 'Asia/Kolkata', 'DD Mon, HH24:MI')
  ) order by m.created_at), '[]'::jsonb)
  into v_msgs
  from referral_messages m where m.referral_id = v_rid;

  return jsonb_build_object('ok', true, 'messages', v_msgs);
end; $$;

revoke all on function public.get_referral_messages(text, uuid) from public;
grant execute on function public.get_referral_messages(text, uuid) to anon, authenticated;

-- ---------- post message ----------
create or replace function public.post_referral_message(p_code text, p_referral uuid, p_body text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_rid uuid; v_count int;
begin
  v_rid := _partner_referral(p_code, p_referral);
  if v_rid is null then return jsonb_build_object('ok', false, 'error', 'not_found'); end if;
  if p_body is null or length(trim(p_body)) < 1 or length(p_body) > 2000 then
    return jsonb_build_object('ok', false, 'error', 'invalid_body');
  end if;
  select count(*) into v_count from referral_messages where referral_id = v_rid;
  if v_count >= 500 then return jsonb_build_object('ok', false, 'error', 'thread_full'); end if;

  insert into referral_messages (referral_id, sender, body) values (v_rid, 'partner', trim(p_body));
  update referrals set partner_last_read_at = now() where id = v_rid;
  return jsonb_build_object('ok', true);
end; $$;

revoke all on function public.post_referral_message(text, uuid, text) from public;
grant execute on function public.post_referral_message(text, uuid, text) to anon, authenticated;

-- ---------- dashboard v3: referral id + unread counts ----------
create or replace function public.get_partner_dashboard(p_code text)
returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_partner partners%rowtype; v_result jsonb;
begin
  select * into v_partner from partners
  where upper(code) = upper(trim(p_code)) and active = true;
  if not found then return null; end if;

  select jsonb_build_object(
    'partnerName',        v_partner.name,
    'partnerSince',       v_partner.partner_since,
    'track',              v_partner.track,
    'currentTierPercent', v_partner.tier_percent,
    'referrals', coalesce(jsonb_agg(
      jsonb_build_object(
        'id',                 r.id,
        'business',           r.business,
        'city',               r.city,
        'contactName',        r.contact_name,
        'introducedOn',       r.introduced_on,
        'submittedOn',        to_char(r.created_at at time zone 'Asia/Kolkata', 'YYYY-MM-DD HH24:MI'),
        'submittedByPartner', r.submitted_by_partner,
        'refId',              substring(r.id::text, 1, 8),
        'stage',              r.stage,
        'projectValue',       r.project_value,
        'sharePercent',       r.share_percent,
        'paidAmount',         coalesce(p.paid_total, 0),
        'lastPaidDate',       p.last_paid,
        'messageCount',       coalesce(m.msg_count, 0),
        'unreadMessages',     coalesce(m.unread_admin_msgs, 0)
      ) order by r.created_at desc
    ) filter (where r.id is not null), '[]'::jsonb)
  )
  into v_result
  from referrals r
  left join (
    select referral_id, sum(amount) as paid_total, max(paid_on) as last_paid
    from partner_payments group by referral_id
  ) p on p.referral_id = r.id
  left join (
    select rm.referral_id,
           count(*) as msg_count,
           count(*) filter (where rm.sender = 'admin' and rm.created_at > r2.partner_last_read_at) as unread_admin_msgs
    from referral_messages rm join referrals r2 on r2.id = rm.referral_id
    group by rm.referral_id
  ) m on m.referral_id = r.id
  where r.partner_id = v_partner.id;

  return v_result;
end; $$;

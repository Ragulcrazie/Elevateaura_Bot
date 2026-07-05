-- ============================================================
-- Migration 2: partners can submit leads directly from the portal
-- Run once in Supabase SQL Editor, AFTER partner_program_schema.sql
-- ============================================================

alter table public.referrals add column if not exists contact_name  text;
alter table public.referrals add column if not exists contact_phone text;
alter table public.referrals add column if not exists submitted_by_partner boolean not null default false;

-- ---------- PARTNER LEAD SUBMISSION RPC ----------
-- Anon-callable with a valid active partner code. Server timestamps the
-- record (created_at), so the submission date is provable and the 90-day
-- protection window starts automatically. Spam guard: max 20 open
-- 'introduced' leads per partner.

create or replace function public.submit_referral(
  p_code          text,
  p_business      text,
  p_contact_name  text default null,
  p_contact_phone text default null,
  p_city          text default null,
  p_notes         text default null
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_partner partners%rowtype;
  v_open    int;
  v_id      uuid;
begin
  select * into v_partner
  from partners
  where upper(code) = upper(trim(p_code)) and active = true;

  if not found then
    return jsonb_build_object('ok', false, 'error', 'invalid_code');
  end if;

  if p_business is null or length(trim(p_business)) < 3 then
    return jsonb_build_object('ok', false, 'error', 'invalid_business');
  end if;

  select count(*) into v_open
  from referrals
  where partner_id = v_partner.id and stage = 'introduced';

  if v_open >= 20 then
    return jsonb_build_object('ok', false, 'error', 'too_many_open');
  end if;

  insert into referrals
    (partner_id, business, city, contact_name, contact_phone, notes,
     stage, share_percent, submitted_by_partner)
  values
    (v_partner.id, trim(p_business), nullif(trim(coalesce(p_city,'')),''),
     nullif(trim(coalesce(p_contact_name,'')),''),
     nullif(trim(coalesce(p_contact_phone,'')),''),
     nullif(trim(coalesce(p_notes,'')),''),
     'introduced', v_partner.tier_percent, true)
  returning id into v_id;

  return jsonb_build_object('ok', true, 'id', v_id, 'ref', substring(v_id::text, 1, 8));
end;
$$;

revoke all on function public.submit_referral(text,text,text,text,text,text) from public;
grant execute on function public.submit_referral(text,text,text,text,text,text) to anon, authenticated;

-- ---------- DASHBOARD RPC v2: include proof fields ----------

create or replace function public.get_partner_dashboard(p_code text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_partner partners%rowtype;
  v_result  jsonb;
begin
  select * into v_partner
  from partners
  where upper(code) = upper(trim(p_code)) and active = true;

  if not found then
    return null;
  end if;

  select jsonb_build_object(
    'partnerName',        v_partner.name,
    'partnerSince',       v_partner.partner_since,
    'track',              v_partner.track,
    'currentTierPercent', v_partner.tier_percent,
    'referrals', coalesce(jsonb_agg(
      jsonb_build_object(
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
        'lastPaidDate',       p.last_paid
      ) order by r.created_at desc
    ) filter (where r.id is not null), '[]'::jsonb)
  )
  into v_result
  from referrals r
  left join (
    select referral_id, sum(amount) as paid_total, max(paid_on) as last_paid
    from partner_payments group by referral_id
  ) p on p.referral_id = r.id
  where r.partner_id = v_partner.id;

  return v_result;
end;
$$;

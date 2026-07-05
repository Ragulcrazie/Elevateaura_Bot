-- ============================================================
-- Elevate Aura Partner Program: partners + referrals + payments
-- Run this once in Supabase SQL Editor (same project as admin.html:
-- https://mdfsxdyfndbqemibwvad.supabase.co)
-- Admin access = raguls09@gmail.com (same login as admin.html)
-- Partner access = read-only dashboard via secure RPC with their code
-- ============================================================

-- ---------- TABLES ----------

create table if not exists public.partners (
  id            uuid primary key default gen_random_uuid(),
  code          text not null unique,                       -- e.g. EA-9X4KQ72M
  name          text not null,
  phone         text,
  track         text not null default 'referral'
                check (track in ('referral','distribution')),
  tier_percent  numeric not null default 10,
  partner_since date not null default current_date,
  active        boolean not null default true,
  notes         text,
  created_at    timestamptz not null default now()
);

create table if not exists public.referrals (
  id             uuid primary key default gen_random_uuid(),
  partner_id     uuid not null references public.partners(id) on delete cascade,
  business       text not null,
  city           text,
  introduced_on  date not null default current_date,
  stage          text not null default 'introduced'
                 check (stage in ('introduced','first-call','demo','proposal','signed','delivered','not-closed')),
  project_value  numeric not null default 0,
  share_percent  numeric not null default 10,
  notes          text,
  created_at     timestamptz not null default now()
);

create table if not exists public.partner_payments (
  id           uuid primary key default gen_random_uuid(),
  referral_id  uuid not null references public.referrals(id) on delete cascade,
  amount       numeric not null,
  paid_on      date not null default current_date,
  txn_ref      text,
  created_at   timestamptz not null default now()
);

create index if not exists idx_referrals_partner on public.referrals(partner_id);
create index if not exists idx_payments_referral on public.partner_payments(referral_id);

-- ---------- ROW LEVEL SECURITY ----------
-- Admin (raguls09@gmail.com) gets full access. Nobody else can touch tables directly.
-- Partners never query tables; they use the RPC below with their private code.

alter table public.partners        enable row level security;
alter table public.referrals       enable row level security;
alter table public.partner_payments enable row level security;

drop policy if exists admin_all_partners  on public.partners;
drop policy if exists admin_all_referrals on public.referrals;
drop policy if exists admin_all_payments  on public.partner_payments;

create policy admin_all_partners on public.partners
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'raguls09@gmail.com')
  with check ((auth.jwt() ->> 'email') = 'raguls09@gmail.com');

create policy admin_all_referrals on public.referrals
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'raguls09@gmail.com')
  with check ((auth.jwt() ->> 'email') = 'raguls09@gmail.com');

create policy admin_all_payments on public.partner_payments
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'raguls09@gmail.com')
  with check ((auth.jwt() ->> 'email') = 'raguls09@gmail.com');

-- ---------- PARTNER DASHBOARD RPC ----------
-- Anon-callable. Returns one partner's dashboard as JSON, only if the code matches
-- an active partner. security definer bypasses RLS inside the function only.

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
        'business',     r.business,
        'city',         r.city,
        'introducedOn', r.introduced_on,
        'stage',        r.stage,
        'projectValue', r.project_value,
        'sharePercent', r.share_percent,
        'paidAmount',   coalesce(p.paid_total, 0),
        'lastPaidDate', p.last_paid
      ) order by r.introduced_on desc
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

revoke all on function public.get_partner_dashboard(text) from public;
grant execute on function public.get_partner_dashboard(text) to anon, authenticated;

-- ---------- DEMO PARTNER (safe to delete later) ----------
insert into public.partners (code, name, track, tier_percent, partner_since)
values ('EA-DEMO2026', 'Demo Partner', 'referral', 15, '2026-05-02')
on conflict (code) do nothing;

insert into public.referrals (partner_id, business, city, introduced_on, stage, project_value, share_percent)
select id, x.business, x.city, x.introduced_on::date, x.stage, x.project_value, x.share_percent
from public.partners p,
 (values
   ('Sunrise Diagnostics',      'Chennai',    '2026-05-10', 'delivered', 290000, 10),
   ('Sri Meditech Distributors','Coimbatore', '2026-05-28', 'signed',    340000, 10),
   ('Green Cross Scan Centre',  'Madurai',    '2026-06-20', 'proposal',  310000, 15),
   ('Velan Ortho Clinic',       'Chennai',    '2026-06-29', 'first-call',     0, 15)
 ) as x(business, city, introduced_on, stage, project_value, share_percent)
where p.code = 'EA-DEMO2026'
  and not exists (select 1 from public.referrals r where r.partner_id = p.id);

insert into public.partner_payments (referral_id, amount, paid_on, txn_ref)
select r.id, x.amount, x.paid_on::date, x.txn_ref
from public.referrals r
join public.partners p on p.id = r.partner_id and p.code = 'EA-DEMO2026',
 (values
   ('Sunrise Diagnostics',       29000, '2026-06-18', 'UPI-982314'),
   ('Sri Meditech Distributors', 13600, '2026-06-25', 'UPI-993471')
 ) as x(business, amount, paid_on, txn_ref)
where r.business = x.business
  and not exists (select 1 from public.partner_payments pp where pp.referral_id = r.id);

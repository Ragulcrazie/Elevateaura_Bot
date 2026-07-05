# Partner Program: Setup & Daily Use

Two connected pages, one Supabase backend (same project and same admin login as `admin.html`).

| Page | Who uses it | Access |
|---|---|---|
| `partner-admin.html` | You only | Login: raguls09@gmail.com (same as applications admin) |
| `partner-portal.html` | Partners | Private code, e.g. `?code=EA-9X4KQ72M` |

## One-time setup (5 minutes)

1. Open Supabase dashboard -> project `mdfsxdyfndbqemibwvad` -> SQL Editor.
2. Paste and run `setup/partner_program_schema.sql` (this whole file, once).
3. Commit and push the website repo (partner-admin.html, partner-portal.html, setup/).
4. Test:
   - Open `elevateaura.co.in/partner-admin.html`, sign in. You should see the demo partner.
   - Open `elevateaura.co.in/partner-portal.html?code=EA-DEMO2026`. You should see the demo dashboard.

## Daily workflow

1. New partner agrees -> partner-admin -> "+ Add partner" (code is auto-generated).
2. Click "Copy link" or "WhatsApp" to send them their private portal link.
3. They introduce a business -> select the partner -> "+ Add referral".
4. As the deal moves -> change the Stage dropdown (updates their portal instantly).
5. Client pays you -> "+ Payment" on that referral -> enter amount + UPI/NEFT ref.
   The partner sees paid amount and date on their portal immediately.

## Security model

- Tables are RLS-locked: only the authenticated admin email can read/write.
- Partners never touch the tables. The portal calls one function
  (`get_partner_dashboard`) that returns only their own data, only if their
  code matches an active partner. Deactivate a partner to cut access instantly.
- The key in the pages is the publishable (anon) key: safe in client code.

## Notes

- The static files in `assets/partners/*.json` are now only a fallback/demo.
  After the SQL is run, Supabase data always wins. You can delete the demo
  partner from Supabase once real partners exist.
- Later upgrade (optional): move partners to real logins with Supabase Auth
  if you cross ~15 active partners.

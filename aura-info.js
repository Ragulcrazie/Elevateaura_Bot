/* Aura Business, per-module info tooltips (what · who · why) */
const MODULE_INFO = {
  // Suite 1, CRM & Sales
  "Leads & Pipeline": "Track every enquiry from first contact to close. For sales reps and owners, so no lead slips and you always know what's in the pipeline.",
  "Customer / Hospital Accounts": "A single record for every hospital, clinic and dealer with GSTIN and contacts. For sales and service, one source of truth for who you sell to.",
  "Contacts & Decision-Makers": "Map the doctors, purchase heads and admins inside each account. For reps, so you always reach the person who signs off.",
  "Field Visits + GPS check-in": "Log site visits with a GPS check-in. For owners managing field reps, proof of visits and where your team actually went.",
  "Sample Tracking": "Track demo units given out, returned or converted. For sales, so costly samples don't vanish and you chase conversions.",
  "Activity Feed / Rep log": "A daily timeline of every rep's calls, visits and updates. For managers, see who's working without asking.",
  "Territory & Target Management": "Assign areas and monthly targets, track actual vs target. For owners, keep every rep accountable to a number.",
  "Lead-Source & Conversion Analytics": "See which sources and reps actually convert. For owners, spend effort where the wins come from.",
  // Suite 2, Billing
  "GST Quotation Builder": "Build itemised, GST-correct quotes and print a clean PDF. For sales and back-office, send professional quotes in minutes.",
  "Sales Orders": "Turn an accepted quote into an order in one click. For operations, a clear record of what's committed to deliver.",
  "Tax Invoice (GST, PDF)": "Gapless, GST-compliant tax invoices with CGST/SGST/IGST and a printable PDF. For accounts, legal invoices your CA accepts.",
  "Delivery Challan": "Generate delivery challans against orders. For dispatch, proper paperwork when goods leave your premises.",
  "Payments & Receipts": "Record payments against invoices and print receipts; auto-marks invoices paid. For accounts, always know what's collected.",
  "Payment Tracker + reminders": "Chase dues with WhatsApp reminders. For owners, get your stuck money in faster without manual follow-up.",
  "E-Invoice (IRN / QR)": "Capture and generate IRN and QR for B2B invoices. For larger distributors, stay e-invoice compliant as you scale.",
  "E-Way Bill": "Record and generate e-way bills for goods movement. For dispatch, avoid penalties on inter-state and high-value shipments.",
  "Credit Notes / Returns": "Issue credit notes against invoices for returns. For accounts, handle returns the compliant way, not by editing invoices.",
  // Suite 3, Inventory
  "Product Catalog & Lookup": "Your full product list with HSN, MRP and GST rate. For everyone, quotes, invoices and stock all pull from one catalog.",
  "Brand & Authorization": "Track the brands you carry and your authorisation status. For tenders and sales, prove you're an authorised dealer.",
  "Serial / Unit-level Stock": "Track individual units by serial number. For medical equipment, know exactly which unit went where.",
  "Stock Movements / Ledger": "Every stock IN and OUT in one ledger with live on-hand. For stores, figures that match reality.",
  "Multi-Warehouse": "Hold stock across multiple locations. For multi-branch distributors, see stock per warehouse.",
  "Batch & Expiry Tracking": "Track batches and expiry dates. For consumables and reagents, sell oldest first and avoid expired stock.",
  "Low-Stock & Reorder Alerts": "Flags products at or below their reorder level. For purchase, never lose a sale to 'out of stock'.",
  "Barcode / QR Scan": "Scan items in and out. For warehouse staff, faster, error-free stock movement.",
  // Suite 4, AMC
  "Service Contracts (AMC)": "Manage every AMC with term, value and coverage. For service teams, your recurring-revenue backbone in one place.",
  "CMC Contracts": "Comprehensive contracts that include parts. For service, track CMC margin and parts coverage separately from AMC.",
  "Warranty Tracking": "Know each asset's warranty status. For service, bill correctly and never give free service on a chargeable job.",
  "Preventive Maintenance Schedules": "Auto-schedules PM visits across the contract term. For service managers, planned maintenance that runs itself.",
  "SLA Definitions & Breach Tracking": "Set response and resolution targets and catch breaches. For service, protect the SLAs hospitals hold you to.",
  "Service Invoices": "Bill AMC, CMC and chargeable service. For accounts, turn service work into invoiced revenue.",
  "Contract Renewal Engine": "Flags contracts before they expire and reminds you to renew. For owners, stop the No.1 hidden revenue leak.",
  "Asset / Installed-Base Register": "Every machine you've installed, with its service history. For service, the foundation for AMC upsell and renewals.",
  "AMC Revenue & Leakage Dashboard": "Shows AMC book value and lapsed-renewal revenue in ₹. For owners, see exactly how much money is leaking.",
  // Suite 5, FSM
  "Breakdown / Service Call Intake": "Log breakdown calls with priority and asset. For service desks, nothing gets missed or forgotten.",
  "Technician Dispatch": "Assign the right technician to each call. For service managers, coordinate the field team from one screen.",
  "Mobile Job Card": "Technicians record work done and parts used on their phone. For field staff, close jobs on site.",
  "Spare Parts Used per Job": "Capture spares consumed on each job; auto-decrements stock. For owners, spare revenue and stock control in one.",
  "Service History per Asset": "Every service event against each machine. For service, proof of care that wins renewals.",
  "Field Signature & Job-Done": "Capture the customer's sign-off on completion. For service, undisputed proof the job was done.",
  "Technician Route / Schedule": "See each technician's day and route. For managers, plan visits efficiently.",
  // Suite 6, Helpdesk
  "Ticket Management": "Log and track every customer issue to closure. For support, nothing falls through the cracks.",
  "Ticket Status Workflow": "Move tickets through open, in-progress, resolved, closed. For teams, a clear, consistent process.",
  "Internal Notes / Collaboration": "Private notes on each ticket for your team. For support, keep context without confusing the customer.",
  "SLA Timers on Tickets": "Every ticket on a response and resolution clock. For owners, see breaches before they cost a renewal.",
  "Customer Ticket Submission": "Let customers raise tickets themselves. For support, fewer phone calls, everything logged.",
  "CSAT / Feedback on Close": "Capture a rating when a ticket closes. For owners, measure and prove service quality.",
  // Suite 7, Procurement
  "Supplier Master": "All your suppliers with GSTIN and contacts. For purchase, one place for who you buy from.",
  "Purchase Orders": "Raise itemised POs to suppliers. For purchase, a clear record of what's on order.",
  "Goods Receipt (GRN)": "Receive a PO and auto stock-in every item. For stores, inventory updates itself on receipt.",
  "Supplier Price Lists": "Keep each supplier's prices. For purchase, buy at the right rate every time.",
  "PO Approval Workflow": "Route large POs for approval. For owners, control spend before it happens.",
  "Supplier Payments / Payables": "Track what you owe each supplier. For accounts, pay on time, keep credit healthy.",
  // Suite 8, Tenders
  "Tender Tracker": "Track every government tender with value and deadline. For tender teams, never miss a submission.",
  "Tender Document Vault": "Store tender documents in one place. For bid teams, find papers fast under deadline.",
  "Bid / EMD & Deadline Reminders": "Track EMD and deadlines with alerts. For owners, EMD is real cash; don't miss a refund or a date.",
  "Outcome & Win-Rate Analytics": "See your win rate by authority. For owners, bid where you actually win.",
  "Rate-Contract Management": "Manage standing rate contracts. For sales, apply agreed rates automatically.",
  // Suite 9, HRMS
  "Attendance (Geo + Selfie)": "Mark attendance with location and selfie. For owners of field teams, real presence, not proxy.",
  "Leave Management": "Apply, approve and track leave. For managers, a clean approval trail.",
  "Staff Directory & Profiles": "All employees with roles and salary. For HR, onboard staff and give them logins.",
  "Role-Based Access Control": "Control who can see and do what. For owners, staff see only what they should.",
  "GPS / Field Tracking": "See where field staff are during the day. For managers, coordinate and verify field work.",
  "Staff Verification": "Selfie and ID verification for field staff. For owners, confidence in who's representing you.",
  "Payroll Inputs / Salary Register": "Days present and salary, ready for payroll. For HR and accounts, the inputs your payroll needs.",
  "Shift & Roster Planning": "Plan shifts and rosters. For managers, cover every shift without clashes.",
  // Suite 10, Finance
  "Receivables Ageing": "Outstanding by 0-30, 31-60, 61-90, 90+ days with a chase-first list. For owners, accelerate collections.",
  "Payables Ledger": "What you owe suppliers, aged. For accounts, manage outgoing cash.",
  "Expense Management": "Log and categorise business expenses. For owners, see where money goes.",
  "Cashflow Dashboard": "Money in vs money out at a glance. For owners, know your position daily.",
  "GST Returns Prep (GSTR-1/3B)": "This month's output tax summarised. For your CA, GST filing made simple.",
  "Tally / Accounting Export": "Export data for your accountant. For accounts, no double entry.",
  "P&L by Product Line / Territory": "Revenue minus cost, by segment. For owners, see what's actually profitable.",
  // Suite 11, Portals
  "Customer Self-Service Portal": "A branded portal for customers to self-serve. For service, fewer calls, happier customers.",
  "Distributor / B2B Order Portal": "Let distributors place orders themselves. For sales, orders without phone tag.",
  "Distributor Payment / UTR": "Distributors submit payment and UTR; you verify. For accounts, a clean B2B payment trail.",
  "Order Tracking Page": "A page where customers track their order. For support, fewer 'where's my order' calls.",
  "Quote-Request Inbound": "A public form that drops quote requests into your pipeline. For sales, turn website visitors into leads.",
  "Branded Login + Docs Vault": "Branded customer login with their documents. For service, invoices and reports in one place.",
  // Suite 12, Platform
  "Owner / CEO Dashboard": "Pipeline, cash, AMC and service on one screen. For the owner, your whole business at a glance.",
  "Reports Engine": "Live counts and reports across the platform. For owners, answers without spreadsheets.",
  "Notifications Hub": "All your alerts in one place. For everyone, never miss something important.",
  "WhatsApp Business Integration": "Send updates and reminders on WhatsApp. For India-first teams, reach customers where they are.",
  "Audit Log / Activity Trail": "Who did what, when. For owners, accountability and security.",
  "Tenant Admin & Module Store": "Turn modules on and off and manage your account. For owners, pay only for what you use.",
  "AI Assistant": "Ask questions about your data in plain language. For owners, answers without digging through screens.",
  "Settings, Branding & Org Config": "Your name, logo, GSTIN and preferences. For owners, make it your software.",
};

function auraTip(name){
  var info = MODULE_INFO[name];
  if(!info) return '';
  return '<span class="tip" tabindex="0" onclick="event.preventDefault();event.stopPropagation();this.classList.toggle(\'open\')"><span class="ic">i</span><span class="tipbox">'+info+'</span></span>';
}

// Close any open tooltip when clicking elsewhere.
document.addEventListener('click', function(e){
  if(!e.target.closest('.tip')){
    document.querySelectorAll('.tip.open').forEach(function(t){ t.classList.remove('open'); });
  }
});

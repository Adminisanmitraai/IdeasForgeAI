# ForgeHR Accounts evidence audit — 20 October 2026

## Result and limits

Accounts mode is a conversational mode, not an authorization role. Keep the existing verified active organization membership, active organization check, caller JWT and publishable-key reads. Never use a service key. Every existing role (owner, hr_admin, manager, employee, auditor) remains limited to their own linked active employee. No new organization-wide finance permission is granted.

The source audit found payroll_runs, employee_payslips, employee_compensation, payroll_exceptions and employee_service_requests in ForgeHR's application types and payroll pages/actions. It found no invoice, reimbursement, ledger or bank settlement integration. ForgeHR's authority blueprint says Accounts and Admin / IT roles are proposed and not assignable. The committed migrations do not supply the authoritative employee/payroll baseline. Production management SQL access returned permission denied; no production financial records or policy contents were read, no database changes were attempted, and applied RLS/grants/completeness remain unverified.

Authoritative repository references inspected:
- https://github.com/Ranjanhore/hr-management-saas/blob/db37d21fa8fb9ee29e5164b4776d2803c1567983/src/types/app-database.ts
- https://github.com/Ranjanhore/hr-management-saas/blob/db37d21fa8fb9ee29e5164b4776d2803c1567983/src/app/app/employee/payroll/page.tsx
- https://github.com/Ranjanhore/hr-management-saas/blob/db37d21fa8fb9ee29e5164b4776d2803c1567983/src/app/app/hr/payroll/actions.ts
- https://github.com/Ranjanhore/hr-management-saas/blob/db37d21fa8fb9ee29e5164b4776d2803c1567983/docs/AUTHORITY_HIERARCHY.md
- https://github.com/Ranjanhore/hr-management-saas/blob/db37d21fa8fb9ee29e5164b4776d2803c1567983/supabase/migrations/20260820154500_policy_compliance_v1.sql

## Supported questions

| Question | Authorized source | Interpretation |
| --- | --- | --- |
| What is my recorded gross, deductions or net pay? | Up to three own published employee_payslips | Report record ID and publication date with source ID; no bank-payment claim |
| How many paid or loss-of-pay days are recorded? | days_paid and lop_days on those payslips | Payroll inputs, not attendance or settlement certification |
| What happened to my payroll/reimbursement query? | Up to ten own recent service requests | Ticket status and resolution note only; not verified reimbursement approval/payment |
| What is the reimbursement rule or approval limit? | Accessible published effective hr_policies summary, applicable role/location | Only when explicitly stated; cite title/version/source; not evidence of a transaction |
| Is invoice X paid, when will reimbursement Y arrive, or what is the outstanding balance? | No integrated authoritative source | Cannot verify; refer to service center without claiming zero balance or a payment date |
| Show another employee's salary or all company payments | No assistant authorization | No broader retrieval, including for owners and HR admins |

## Implemented retrieval

Accounts now includes payslip identifiers, publication timestamps, paid days and LOP days. Queries retain organization, employee and published filters and caller credentials. Returned financial rows are checked again for those identifiers/status before a field allowlist removes scope keys and unexpected fields. Accounts service requests include ID and updated timestamp and receive the same tenant/employee recheck. Policy summaries include their record ID and existing version/effective-date fields. Existing policy applicability filtering remains in force.

The context explicitly marks invoice, reimbursement, payment schedule, ledger and bank settlement sources as unintegrated, even when policies are available. Instructions distinguish published payslips and resolved tickets from payment confirmation. Empty/bounded results do not establish company totals. There are no writes or new model tools. HR, Admin, IT, transcription and speech routes remain unchanged.

## Precise integration requirements

Before adding any financial connector, obtain a reviewed sanitized schema/grant/policy/function catalog from the existing authorized operator. Do not retry denied production management routes or substitute another identity. Verify the owner-approved access matrix and publish the relevant company policies with version, effective date, applicable roles/locations and approval owner.

Each connector must provide:
- Stable source system and record ID, organization mapping, currency, amount, record version, last sync time, source update time, deletion/void semantics and reconciliation owner. Never derive tenant membership from a prompt, company name or user-editable metadata.
- Invoices: invoice number, customer/vendor identity appropriate to role, issue/due date, approved amount, credit notes, payment allocations and explicit status semantics. A due date is not a promised payment date.
- Reimbursements: claim ID, employee/organization IDs, submission, approved amount, approval/rejection state and dates, scheduled payment and settlement references when actually available. Employees may see only their claims; Accounts needs an explicitly activated functional permission.
- Payments: schedule ID, related invoice/claim IDs, scheduled versus executed versus settled state, amounts, timestamps, allocation and reversal evidence. Bank reconciliation is required before claiming settlement. Do not send bank account numbers, raw attachments, tax identifiers or bank credentials to the model.
- Ledgers: approved read model, accounting period, posting state, currency and reconciliation/cutoff rules before offering balances or totals. Separate read privileges from prepare/approve/publish permissions.

Use reviewed versioned migrations and RLS (or security-invoker views) for same-tenant relationships, self-only employee reads, restricted Accounts reads and management oversight as explicitly approved. Enforce at the database/API as well as the assistant. Mode selection must never grant rights. Use fixed read-only queries; no model-generated SQL or user-selected table names/URLs. Bound results and disclose pagination and stale/error states. Cite stable record IDs, observed timestamps and existing authorized UI routes; never fetch arbitrary evidence URLs.

## Verification and release

Offline unit tests cover all five roles, caller credentials, tenant/self filters, rejection of foreign-tenant/other-employee/draft payslips, allowlisted financial fields, source metadata, no-profile/no-payroll access and denied reads. Existing chat, policy, HR/IT and voice regressions must also pass. These mocks do not certify live RLS or generated-model adherence.

Before production release, the authorized operator must validate the unchanged and newly selected fields/grants with synthetic sessions in two isolated organizations: employee, owner, HR admin, manager, auditor; foreign IDs; suspended memberships/organizations; missing profiles; drafts; missing sources; published/current/applicable policies; direct Data API denial. Inspect actual model answers for correct record references, no payment inference, prompt injection resistance and all three supported languages. Validate the existing voice flow separately. No live deployment or schema activation is part of this change.

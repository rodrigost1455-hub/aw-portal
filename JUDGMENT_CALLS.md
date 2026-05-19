# Judgment Calls — AW Client Report Portal

## For Loom walkthrough reference

---

### 1. Visual layout — SACS PDF
The SACS PDF layout was recreated entirely from PRD text descriptions and timestamp references.
No sample PDFs or design mockups were provided. Key decisions:
- Three-element flow: Inflow circle → arrow → Outflow circle → arrow → Private Reserve box
- Fixed 850px page width so no element shifts regardless of dollar amount length
- Progress bar added to Private Reserve box to show % of target funded (PRD implied this was desired)

---

### 2. Happy path prioritized
The complete end-to-end demo path is fully working:
1. Land on client list → see seeded James & Patricia Williams
2. Click "Generate Report" → enter balances → watch live totals update in real time
3. Save report → click "SACS PDF" → download polished PDF

---

### 3. TCC PDF deferred
The TCC (Total Client Composite) PDF layout requires a dynamic bubble grid that scales from
1–6 accounts per account type. Rendering this correctly in WeasyPrint within the 2-hour
constraint was not feasible. Deferred as out-of-scope for this demo.

---

### 4. Canva export deferred
The PRD marks Canva export as a nice-to-have and notes Rebecca's preference is the portal PDF
itself. Deferred — no Canva API integration attempted.

---

### 5. Private Reserve Target storage
Stored on the Client model at creation time as `6 × monthly_expense_budget`.
If the expense budget is later edited, the target is recalculated on save.
Not recalculated per-report — it is a profile-level setting as the PRD describes.

---

### 6. Liabilities excluded from Net Worth
Liabilities are tracked and displayed in a separate section both on the report form and in
the SACS PDF. They are explicitly **never subtracted** from Grand Total Net Worth, per
Rebecca's explicit instruction in the PRD.
Formula used: `Grand Total = C1_retirement + C2_retirement + Non-Retirement + Trust`

---

### 7. Joint retirement account split
The PRD assigns retirement totals to C1 or C2 by owner. For accounts owned `joint`,
the balance is split 50/50 between C1 and C2 retirement totals. This was not specified
in the PRD and is a judgment call — flagged here for review.

---

### 8. No authentication
Auth is explicitly out of scope per PRD. The portal is treated as a trusted internal tool.

---

### 9. No CDN imports
All styling uses system-ui font stack and local static files only. No Google Fonts,
no external CSS/JS libraries. Compatible with Railway's potential firewall restrictions.

---

### 10. Database auto-init + seed on startup
`create_all` runs on every startup (idempotent). Seed data is inserted only if zero
clients exist, so the demo client appears immediately on first launch without
manual setup.

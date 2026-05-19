from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import datetime
import os

from database import engine, get_db, Base, SessionLocal
import models

# Initialize DB
Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="AW Client Report Portal")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ── Seed data ──────────────────────────────────────────────────────────────────
def seed_demo_client():
    db = SessionLocal()
    try:
        if db.query(models.Client).count() == 0:
            client = models.Client(
                full_name="James Williams",
                spouse_name="Patricia Williams",
                dob="1965-03-12",
                spouse_dob="1967-07-28",
                ssn_last4="4421",
                spouse_ssn_last4="8834",
                monthly_salary=15000.0,
                monthly_expense_budget=11000.0,
                private_reserve_target=66000.0,  # 6 × 11,000
            )
            db.add(client)
            db.flush()

            accounts = [
                models.Account(client_id=client.id, owner="client2", type="IRA",
                               account_last4="1122", is_retirement=True),
                models.Account(client_id=client.id, owner="client1", type="RothIRA",
                               account_last4="3344", is_retirement=True),
                models.Account(client_id=client.id, owner="joint", type="brokerage",
                               account_last4="5566", is_retirement=False),
                models.Account(client_id=client.id, owner="joint", type="trust",
                               account_last4="7788", is_trust=True),
                models.Account(client_id=client.id, owner="joint", type="liability",
                               account_last4="9900", is_liability=True, interest_rate=3.5),
            ]
            db.add_all(accounts)
            db.commit()
    finally:
        db.close()


seed_demo_client()


# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(value: float) -> str:
    """Format float as $X,XXX"""
    return f"${value:,.0f}"


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    clients = db.query(models.Client).order_by(models.Client.created_at.desc()).all()
    client_data = []
    for c in clients:
        last_report = (
            db.query(models.QuarterlyReport)
            .filter(models.QuarterlyReport.client_id == c.id)
            .order_by(models.QuarterlyReport.year.desc(), models.QuarterlyReport.quarter.desc())
            .first()
        )
        client_data.append({"client": c, "last_report": last_report})
    return templates.TemplateResponse(request=request, name="index.html", context={"client_data": client_data})


@app.get("/clients/new", response_class=HTMLResponse)
def new_client_form(request: Request):
    return templates.TemplateResponse(request=request, name="client_form.html", context={"client": None})


@app.get("/clients/{client_id}/edit", response_class=HTMLResponse)
def edit_client_form(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    return templates.TemplateResponse(request=request, name="client_form.html", context={"client": client})


@app.post("/clients", response_class=RedirectResponse)
async def create_client(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    expense_budget = float(form.get("monthly_expense_budget", 0))
    client = models.Client(
        full_name=form.get("full_name"),
        spouse_name=form.get("spouse_name") or None,
        dob=form.get("dob"),
        spouse_dob=form.get("spouse_dob") or None,
        ssn_last4=form.get("ssn_last4"),
        spouse_ssn_last4=form.get("spouse_ssn_last4") or None,
        monthly_salary=float(form.get("monthly_salary", 0)),
        monthly_expense_budget=expense_budget,
        private_reserve_target=6 * expense_budget,
    )
    db.add(client)
    db.flush()

    # Process accounts from form
    acct_owners = form.getlist("acct_owner[]")
    acct_types = form.getlist("acct_type[]")
    acct_last4s = form.getlist("acct_last4[]")
    acct_retirements = form.getlist("acct_retirement[]")
    acct_trusts = form.getlist("acct_trust[]")
    acct_liabilities = form.getlist("acct_liability[]")
    acct_rates = form.getlist("acct_rate[]")

    for i in range(len(acct_owners)):
        if not acct_owners[i]:
            continue
        is_ret = str(i) in acct_retirements
        is_trust = str(i) in acct_trusts
        is_liab = str(i) in acct_liabilities
        rate_str = acct_rates[i] if i < len(acct_rates) else ""
        account = models.Account(
            client_id=client.id,
            owner=acct_owners[i],
            type=acct_types[i] if i < len(acct_types) else "brokerage",
            account_last4=acct_last4s[i] if i < len(acct_last4s) else None,
            is_retirement=is_ret,
            is_trust=is_trust,
            is_liability=is_liab,
            interest_rate=float(rate_str) if rate_str else None,
        )
        db.add(account)

    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/clients/{client_id}/report", response_class=HTMLResponse)
def report_form(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    accounts = db.query(models.Account).filter(models.Account.client_id == client_id).all()

    # Get last report for reference balances
    last_report = (
        db.query(models.QuarterlyReport)
        .filter(models.QuarterlyReport.client_id == client_id)
        .order_by(models.QuarterlyReport.year.desc(), models.QuarterlyReport.quarter.desc())
        .first()
    )

    last_balances = {}
    if last_report:
        for ab in last_report.account_balances:
            last_balances[ab.account_id] = ab.balance

    now = datetime.datetime.utcnow()
    current_quarter = (now.month - 1) // 3 + 1
    current_year = now.year

    return templates.TemplateResponse(request=request, name="report_form.html", context={
        "client": client,
        "accounts": accounts,
        "last_balances": last_balances,
        "last_report": last_report,
        "current_quarter": current_quarter,
        "current_year": current_year,
    })


@app.post("/clients/{client_id}/report", response_class=RedirectResponse)
async def save_report(client_id: int, request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    client = db.query(models.Client).filter(models.Client.id == client_id).first()

    inflow = float(form.get("inflow", 0))
    outflow = float(form.get("outflow", 0))
    excess = inflow - outflow

    private_reserve_balance = float(form.get("private_reserve_balance", 0))
    quarter = int(form.get("quarter", 1))
    year = int(form.get("year", datetime.datetime.utcnow().year))

    accounts = db.query(models.Account).filter(models.Account.client_id == client_id).all()

    c1_retirement_total = 0.0
    c2_retirement_total = 0.0
    non_retirement_total = 0.0
    trust_value = 0.0
    liabilities_total = 0.0

    balances_map = {}
    for acct in accounts:
        raw = form.get(f"balance_{acct.id}", "0")
        try:
            bal = float(raw)
        except ValueError:
            bal = 0.0
        balances_map[acct.id] = bal

        if acct.is_liability:
            liabilities_total += bal
        elif acct.is_trust:
            trust_value += bal
        elif acct.is_retirement and acct.owner == "client1":
            c1_retirement_total += bal
        elif acct.is_retirement and acct.owner == "client2":
            c2_retirement_total += bal
        elif acct.is_retirement and acct.owner == "joint":
            # Joint retirement split evenly for display
            c1_retirement_total += bal / 2
            c2_retirement_total += bal / 2
        else:
            non_retirement_total += bal

    grand_total = c1_retirement_total + c2_retirement_total + non_retirement_total + trust_value

    report = models.QuarterlyReport(
        client_id=client_id,
        quarter=quarter,
        year=year,
        inflow=inflow,
        outflow=outflow,
        excess=excess,
        private_reserve_balance=private_reserve_balance,
        c1_retirement_total=c1_retirement_total,
        c2_retirement_total=c2_retirement_total,
        non_retirement_total=non_retirement_total,
        trust_value=trust_value,
        liabilities_total=liabilities_total,
        grand_total_net_worth=grand_total,
    )
    db.add(report)
    db.flush()

    for acct_id, bal in balances_map.items():
        ab = models.AccountBalance(report_id=report.id, account_id=acct_id, balance=bal)
        db.add(ab)

    db.commit()

    form_action = form.get("form_action", "save")
    if form_action == "generate_pdf":
        return RedirectResponse(
            url=f"/clients/{client_id}/report/{report.id}/sacs-pdf",
            status_code=303
        )
    return RedirectResponse(url="/", status_code=303)


@app.get("/clients/{client_id}/report/{report_id}/sacs-pdf", response_class=HTMLResponse)
def generate_sacs_pdf(client_id: int, report_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    report = db.query(models.QuarterlyReport).filter(models.QuarterlyReport.id == report_id).first()
    return templates.TemplateResponse(request=request, name="sacs_pdf.html", context={
        "client": client,
        "report": report,
        "fmt": fmt,
        "quarter_label": f"Q{report.quarter} {report.year}",
    })


# Convenience: generate PDF from latest report
@app.get("/clients/{client_id}/sacs-pdf/latest")
def latest_sacs_pdf(client_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(models.QuarterlyReport)
        .filter(models.QuarterlyReport.client_id == client_id)
        .order_by(models.QuarterlyReport.year.desc(), models.QuarterlyReport.quarter.desc())
        .first()
    )
    if not report:
        return HTMLResponse("<h2>No report found for this client.</h2>", status_code=404)
    return RedirectResponse(url=f"/clients/{client_id}/report/{report.id}/sacs-pdf")

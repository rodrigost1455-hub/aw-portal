from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    spouse_name = Column(String, nullable=True)
    dob = Column(String, nullable=False)
    spouse_dob = Column(String, nullable=True)
    ssn_last4 = Column(String(4), nullable=False)
    spouse_ssn_last4 = Column(String(4), nullable=True)
    monthly_salary = Column(Float, nullable=False)
    monthly_expense_budget = Column(Float, nullable=False)
    private_reserve_target = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    accounts = relationship("Account", back_populates="client", cascade="all, delete-orphan")
    reports = relationship("QuarterlyReport", back_populates="client", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    owner = Column(String, nullable=False)  # client1 / client2 / joint
    type = Column(String, nullable=False)   # IRA/RothIRA/401K/brokerage/trust/liability
    account_last4 = Column(String(4), nullable=True)
    is_retirement = Column(Boolean, default=False)
    is_trust = Column(Boolean, default=False)
    is_liability = Column(Boolean, default=False)
    interest_rate = Column(Float, nullable=True)

    client = relationship("Client", back_populates="accounts")
    balances = relationship("AccountBalance", back_populates="account", cascade="all, delete-orphan")


class QuarterlyReport(Base):
    __tablename__ = "quarterly_reports"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    quarter = Column(Integer, nullable=False)   # 1-4
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inflow = Column(Float, nullable=False)
    outflow = Column(Float, nullable=False)
    excess = Column(Float, nullable=False)

    private_reserve_balance = Column(Float, default=0.0)
    schwab_balance = Column(Float, default=0.0)

    c1_retirement_total = Column(Float, default=0.0)
    c2_retirement_total = Column(Float, default=0.0)
    non_retirement_total = Column(Float, default=0.0)
    trust_value = Column(Float, default=0.0)
    liabilities_total = Column(Float, default=0.0)
    grand_total_net_worth = Column(Float, default=0.0)

    client = relationship("Client", back_populates="reports")
    account_balances = relationship("AccountBalance", back_populates="report", cascade="all, delete-orphan")


class AccountBalance(Base):
    __tablename__ = "account_balances"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("quarterly_reports.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    balance = Column(Float, default=0.0)

    report = relationship("QuarterlyReport", back_populates="account_balances")
    account = relationship("Account", back_populates="balances")

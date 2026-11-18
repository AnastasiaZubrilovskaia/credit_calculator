import pytest
from datetime import date
from decimal import Decimal

from calculator.app.services.loan_terms import (
    PrescoringError,
    check_prescoring,
    calculate_rate,
    calculate_total_amount,
)

TODAY = date(2026, 11, 1)


def test_prescoring_passed():
    check_prescoring(birthdate=date(2005, 5, 11),  amount=Decimal("300000"),  today=TODAY)

def test_calculate_rate_base():
    rate = calculate_rate(is_insurance_enabled=False, is_salary_client=False)
    assert rate == Decimal("20.0")

def test_calculate_rate_insurance_only():
    rate = calculate_rate(is_insurance_enabled=True, is_salary_client=False)
    assert rate == Decimal("17.0")

def test_calculate_rate_salary_only():
    rate = calculate_rate(is_insurance_enabled=False, is_salary_client=True)
    assert rate == Decimal("19.0")

def test_calculate_rate_both():
    rate = calculate_rate(is_insurance_enabled=True, is_salary_client=True)
    assert rate == Decimal("16.0")


def test_calculate_total_amount_without_insurance():
    total = calculate_total_amount(amount=Decimal("300000"), is_insurance_enabled=False)
    assert total == Decimal("300000.00")

def test_calculate_total_amount_with_insurance():
    total = calculate_total_amount(amount=Decimal("300000"), is_insurance_enabled=True)
    assert total == Decimal("400000.00")
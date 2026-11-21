from datetime import date
from decimal import Decimal

from calculator.app.services.math import (
    _calculate_payment_schedule,
    _calculate_psk, _calculate_rate, _calculate_total_amount
)



def test_payment_schedule_length_and_dates():
    start = date(2026, 1, 1)
    payment, schedule = _calculate_payment_schedule(Decimal("120000"), Decimal("12"), 12, start)
    assert len(schedule) == 12
    assert schedule[0]["date"] == date(2026, 2, 1)
    assert schedule[-1]["date"] == date(2027, 1, 1)


def test_payment_schedule_balance_is_zero():
    payment, schedule = _calculate_payment_schedule(Decimal("300000"), Decimal("20"), 24)
    last_row = schedule[-1]
    assert last_row["remainingDebt"] == Decimal("0.00")


def test_payment_schedule_total_debt():
    principal = Decimal("300000")
    _, schedule = _calculate_payment_schedule(principal, Decimal("20"), 24)

    total_debt_paid = sum((row["debtPayment"] for row in schedule), Decimal("0"))
    assert total_debt_paid == principal


def test_calculate_simple_psk_without_insurance():
    psk = _calculate_psk(
        amount=Decimal("300000"),
        term=24,
        monthly_payment=Decimal("15000"),
        insurance_cost=Decimal("0")
    )
    assert psk == Decimal("10.000")


def test_calculate_simple_psk_with_insurance():
    psk = _calculate_psk(
        amount=Decimal("300000"),
        term=24,
        monthly_payment=Decimal("15000"),
        insurance_cost=Decimal("100000")
    )
    assert psk == Decimal("26.667")


def test_calculate_rate_base():
    rate = _calculate_rate(is_insurance_enabled=False, is_salary_client=False)
    assert rate == Decimal("20.0")


def test_calculate_rate_insurance_only():
    rate = _calculate_rate(is_insurance_enabled=True, is_salary_client=False)
    assert rate == Decimal("17.0")


def test_calculate_rate_salary_only():
    rate = _calculate_rate(is_insurance_enabled=False, is_salary_client=True)
    assert rate == Decimal("19.0")


def test_calculate_rate_both():
    rate = _calculate_rate(is_insurance_enabled=True, is_salary_client=True)
    assert rate == Decimal("16.0")


def test_calculate_total_amount_without_insurance():
    total = _calculate_total_amount(
        term=24,
        monthly_payment=Decimal("10000"),
        is_insurance_enabled=False
    )
    assert total == Decimal("240000.00")


def test_calculate_total_amount_with_insurance():
    total = _calculate_total_amount(
        term=24,
        monthly_payment=Decimal("10000"),
        is_insurance_enabled=True
    )
    assert total == Decimal("340000.00")
from datetime import date
from decimal import Decimal

import pytest

from calculator.app.services.math import annuity_payment, payment_schedule, calculate_psk


def test_annuity_payment_invalid_input():
    with pytest.raises(ValueError, match="months must be positive"):
        annuity_payment(Decimal("100000"), Decimal("10"), 0)

    with pytest.raises(ValueError, match="principal must be positive"):
        annuity_payment(Decimal("0"), Decimal("10"), 12)


def test_payment_schedule_length_and_dates():
    start = date(2026, 1, 1)
    payment, schedule = payment_schedule(Decimal("120000"), Decimal("12"), 12, start)
    assert len(schedule) == 12
    assert schedule[0]["date"] == date(2026, 2, 1)
    assert schedule[-1]["date"] == date(2027, 1, 1)


def test_payment_schedule_balance_is_zero():
    payment, schedule = payment_schedule(Decimal("300000"), Decimal("20"), 24)
    last_row = schedule[-1]
    assert last_row["remainingDebt"] == Decimal("0.00")


def test_payment_schedule_total_debt():
    principal = Decimal("300000")
    _, schedule = payment_schedule(principal, Decimal("20"), 24)

    total_debt_paid = sum((row["debtPayment"] for row in schedule), Decimal("0"))
    assert total_debt_paid == principal


def test_calculate_simple_psk_without_insurance():
    psk = calculate_psk(principal=Decimal("300000"), annual_rate=Decimal("20"), term_months=24,
                        insurance_cost=Decimal("0"))
    assert psk == Decimal("20.000")


def test_calculate_simple_psk_with_insurance():
    psk = calculate_psk(principal=Decimal("300000"), annual_rate=Decimal("20"), term_months=24,
        insurance_cost=Decimal("100000"))
    assert psk == Decimal("36.667")

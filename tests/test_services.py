import pytest
from datetime import date
from decimal import Decimal

from calculator.app.services.offer_service import create_offers
from calculator.app.services.credit_service import calculate_credit
from calculator.app.services.loan_terms import PrescoringError
from calculator.app.models.dto import (
    LoanStatementRequestDto,
    ScoringDataDto,
    CreditDto,
    LoanOfferDto
)

TODAY = date(2026, 11, 18)


VALID_STATEMENT_DATA = {
    "amount": Decimal("300000"),
    "term": 24,
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "middle_name": "Ivanovich",
    "email": "ivan@example.com",
    "birthdate": date(2001, 11, 11),
    "passport_series": "1234",
    "passport_number": "123456",
}

VALID_SCORING_DATA = {
    "amount": Decimal("300000"),
    "term": 24,
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "middle_name": "Ivanovich",
    "birthdate": date(2001, 11, 11),
    "passport_series": "1234",
    "passport_number": "123456",
    "is_insurance_enabled": True,
    "is_salary_client": False,
}


def test_create_offers_success():
    request = LoanStatementRequestDto(**VALID_STATEMENT_DATA)
    offers = create_offers(request)

    assert len(offers) == 4
    assert all(isinstance(o, LoanOfferDto) for o in offers)
    assert len(set(o.statement_id for o in offers)) == 1


def test_create_offers_sorting():
    request = LoanStatementRequestDto(**VALID_STATEMENT_DATA)
    offers = create_offers(request)

    rates = [o.rate for o in offers]
    assert rates == sorted(rates, reverse=True)
    assert rates[0] == Decimal("20.0")
    assert rates[-1] == Decimal("16.0")


def test_create_offers_prescoring_failed():
    invalid_data = VALID_STATEMENT_DATA.copy()
    invalid_data["birthdate"] = date(2010, 11, 11)
    request = LoanStatementRequestDto(**invalid_data)

    with pytest.raises(PrescoringError):
        create_offers(request)


def test_calculate_credit_success():
    request = ScoringDataDto(**VALID_SCORING_DATA)
    credit = calculate_credit(request, start_date=TODAY)

    assert isinstance(credit, CreditDto)
    assert credit.amount == Decimal("400000.00")
    assert credit.rate == Decimal("17.0")
    assert credit.monthly_payment > 0
    assert credit.psk > 0
    assert len(credit.payment_schedule) == 24



def test_calculate_credit_prescoring_failed():
    invalid_data = VALID_SCORING_DATA.copy()
    invalid_data["amount"] = Decimal("6000000")
    request = ScoringDataDto(**invalid_data)

    with pytest.raises(PrescoringError):
        calculate_credit(request, start_date=TODAY)
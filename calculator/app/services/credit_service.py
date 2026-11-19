import logging
from datetime import date
from decimal import Decimal

from calculator.app.core.config import settings
from calculator.app.models.dto import CreditDto, ScoringDataDto
from calculator.app.services.math import payment_schedule, calculate_psk
from calculator.app.services.loan_terms import calculate_rate, calculate_total_amount, check_prescoring


logger = logging.getLogger(__name__)


def calculate_credit(request: ScoringDataDto, start_date: date | None = None) -> CreditDto:
    issue_date = start_date or date.today()
    logger.info("Calculating credit: amount=%s term=%s insurance=%s salary=%s issue_date=%s",
                request.amount, request.term, request.is_insurance_enabled,
                request.is_salary_client, issue_date)
    check_prescoring(request.birthdate, request.amount, issue_date)
    total = calculate_total_amount(request.amount, request.is_insurance_enabled)
    rate = calculate_rate(request.is_insurance_enabled, request.is_salary_client)

    logger.info("Loan terms: total amount=%s rate=%s%%", total, rate)
    monthly_payment, schedule = payment_schedule(total, rate, request.term, issue_date)
    logger.info("Monthly payment=%s", monthly_payment)

    insurance_amount = settings.insurance_cost if request.is_insurance_enabled else Decimal("0")
    psk = calculate_psk(request.amount, rate, request.term, insurance_amount)
    credit = CreditDto(
        amount=total,
        term=request.term,
        monthly_payment=monthly_payment,
        rate=rate,
        psk=psk,
        is_insurance_enabled=request.is_insurance_enabled,
        is_salary_client=request.is_salary_client,
        payment_schedule=schedule,
    )
    logger.info("Credit calculated: amount=%s term=%s rate=%s monthly_payment=%s psk=%s",
                credit.amount, credit.term, credit.rate, credit.monthly_payment, credit.psk)
    return credit

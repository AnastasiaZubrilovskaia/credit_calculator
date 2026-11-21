import logging
from datetime import date
from decimal import Decimal

from calculator.app.core.config import settings
from calculator.app.models.dto import CreditDto, ScoringDataDto
from calculator.app.services.math import _calculate_payment_schedule, _calculate_psk, _calculate_rate


logger = logging.getLogger(__name__)


def calculate_credit(request: ScoringDataDto, start_date: date | None = None) -> CreditDto:
    issue_date = start_date or date.today()
    logger.info("Calculating credit: amount=%s term=%s insurance=%s salary=%s issue_date=%s",
                request.amount, request.term, request.is_insurance_enabled,
                request.is_salary_client, issue_date)

    rate = _calculate_rate(request.is_insurance_enabled, request.is_salary_client)
    monthly_payment, schedule = _calculate_payment_schedule(request.amount, rate, request.term, issue_date)

    logger.info("Monthly payment=%s", monthly_payment)

    insurance_amount = settings.insurance_cost if request.is_insurance_enabled else Decimal("0")
    psk = _calculate_psk(request.amount, request.term, monthly_payment, insurance_amount)
    credit = CreditDto(
        amount=request.amount,
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

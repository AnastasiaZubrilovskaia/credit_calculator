import logging
from itertools import product
from uuid import uuid4

from calculator.app.models.dto import LoanOfferDto, LoanStatementRequestDto
from calculator.app.services.math import (
    _calculate_annuity_payment,
    _calculate_rate,
    _round_to_kopecks,
    _calculate_total_amount
)

logger = logging.getLogger(__name__)


def create_offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    logger.info("Creating offers: amount=%s term=%s", request.amount, request.term)
    statement_id = uuid4()
    offers = []
    for insurance, salary in product((False, True), repeat=2):
        rate = _calculate_rate(insurance, salary)
        monthly_payment = _calculate_annuity_payment(request.amount, rate, request.term)

        total = _calculate_total_amount(request.term, monthly_payment, insurance)
        offer = LoanOfferDto(
            statement_id=statement_id,
            requested_amount=_round_to_kopecks(request.amount),
            total_amount=total,
            term=request.term,
            monthly_payment=monthly_payment,
            rate=rate,
            is_insurance_enabled=insurance,
            is_salary_client=salary,
        )
        logger.info("Offer built: insurance=%s salary=%s total=%s rate=%s monthly_payment=%s",
                    insurance, salary, offer.total_amount, offer.rate, offer.monthly_payment)
        offers.append(offer)

    offers.sort(key=lambda offer: offer.rate, reverse=True)
    logger.info("Created %d offers for statement %s, rates (worst -> best): %s",
                len(offers), statement_id, [str(o.rate) for o in offers])
    return offers

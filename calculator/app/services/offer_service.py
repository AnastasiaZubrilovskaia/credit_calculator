import logging
from itertools import product
from uuid import uuid4

from calculator.app.models.dto import LoanOfferDto, LoanStatementRequestDto
from calculator.app.services.math import annuity_payment, round_to_kopecks
from calculator.app.services.loan_terms import calculate_rate, calculate_total_amount, check_prescoring


logger = logging.getLogger(__name__)


def create_offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    logger.info("Creating offers: amount=%s term=%s", request.amount, request.term)
    check_prescoring(request.birthdate, request.amount)
    statement_id = uuid4()
    offers = []
    for insurance, salary in product((False, True), repeat=2):
        total = calculate_total_amount(request.amount, insurance)
        rate = calculate_rate(insurance, salary)
        offer = LoanOfferDto(
            statement_id=statement_id,
            requested_amount=round_to_kopecks(request.amount),
            total_amount=total,
            term=request.term,
            monthly_payment=annuity_payment(total, rate, request.term),
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

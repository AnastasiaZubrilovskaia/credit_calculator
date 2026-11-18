import logging

from fastapi import APIRouter

from calculator.app.core.logging_config import mask
from calculator.app.models.dto import LoanOfferDto, LoanStatementRequestDto, CreditDto, ScoringDataDto
from calculator.app.services.credit_service import calculate_credit
from calculator.app.services.offer_service import create_offers

logger = logging.getLogger(__name__)
router = APIRouter()

PRESCORING_ERROR = {400: {"description": "Заявка не прошла прескоринг"}}


@router.post("/offers", response_model=list[LoanOfferDto], responses=PRESCORING_ERROR,
    summary="Расчёт условий кредита",
    response_description="4 предложения, отсортированные от худшего к лучшему",
)
def get_offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    logger.info( "POST /calculator/offers: amount=%s, term=%s, passport=%s/%s",request.amount, request.term,
        mask(request.passport_series), mask(request.passport_number))
    offers = create_offers(request)
    logger.info("POST /calculator/offers: response contains %d offers", len(offers))
    return offers



@router.post( "/calc", response_model=CreditDto, responses=PRESCORING_ERROR,
    summary="Валидация + полный расчет параметров кредита",
    response_description="Параметры кредита, ПСК и график платежей",
)
def calculate(request: ScoringDataDto) -> CreditDto:
    logger.info("POST /calculator/calc: amount=%s, term=%s, passport=%s/%s",request.amount,
        request.term, mask(request.passport_series),  mask(request.passport_number)
    )
    credit = calculate_credit(request)
    logger.info("POST /calculator/calc: response amount=%s monthlyPayment=%s psk=%s, schedule of %s rows",
                credit.amount, credit.monthly_payment, credit.psk, len(credit.payment_schedule))
    return credit
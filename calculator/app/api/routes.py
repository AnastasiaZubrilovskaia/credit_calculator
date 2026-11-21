import logging

from fastapi import APIRouter, HTTPException

from calculator.app.models.dto import LoanOfferDto, LoanStatementRequestDto, CreditDto, ScoringDataDto
from calculator.app.services.credit_service import calculate_credit
from calculator.app.services.offer_service import create_offers

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/offers", response_model=list[LoanOfferDto],
    summary="Расчёт условий кредита",
    response_description="4 предложения, отсортированные от худшего к лучшему",
)
def get_offers(request: LoanStatementRequestDto) -> list[LoanOfferDto]:
    try:
        logger.info( "POST /calculator/offers: Старт скоринга кредитной заявки по клиенту. Сумма: %s, срок: %s",
                     request.amount, request.term)
        offers = create_offers(request)
        logger.info("POST /calculator/offers: Прескоринг кредитной заявки по клиенту успешно завершен")
        return offers
    except Exception as e:
        logger.error("POST /calculator/offers: Внутренняя ошибка сервера: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.post( "/calc", response_model=CreditDto,
    summary="Валидация + полный расчет параметров кредита",
    response_description="Параметры кредита, ПСК и график платежей",
)
def calculate(request: ScoringDataDto) -> CreditDto:
    try:
        logger.info("POST /calculator/calc: Старт скоринга кредитной заявки по клиенту. Сумма: %s, срок: %s",
                    request.amount, request.term
        )
        credit = calculate_credit(request)
        logger.info("POST /calculator/calc: Скоринг кредитной заявки по клиенту успешно завершен")
        return credit
    except Exception as e:
        logger.error("POST /calculator/calc: Внутренняя ошибка сервера: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
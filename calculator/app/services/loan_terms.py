import logging
from datetime import date
from decimal import Decimal

from calculator.app.core.config import settings
from calculator.app.services.math import round_to_kopecks

logger = logging.getLogger(__name__)


class PrescoringError(Exception):
    def __init__(self, reasons: list[str]):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def age_on(birthdate: date, today: date) -> int:
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


#прескоринг
def check_prescoring(birthdate: date, amount: Decimal, today: date | None = None) -> None:
    age = age_on(birthdate, today or date.today())
    logger.info("Prescoring started: age=%s amount=%s (rules: age %s-%s, amount <= %s)",
                age, amount, settings.min_age, settings.max_age, settings.max_amount)
    reasons = []
    if age < settings.min_age:
        reasons.append(f"Person must be at least {settings.min_age} years old")
    if age > settings.max_age:
        reasons.append(f"Person must be at most {settings.max_age} years old")
    if amount > settings.max_amount:
        reasons.append(f"Amount must not be more {settings.max_amount}")
    if reasons:
        logger.warning("Prescoring failed: %s", reasons)
        raise PrescoringError(reasons)
    logger.info("Prescoring passed")

#подсчет итоговой ставки с учетом скидок (наличия страховки, зарплаты)
def calculate_rate(is_insurance_enabled: bool, is_salary_client: bool) -> Decimal:
    rate = settings.base_rate
    if is_insurance_enabled:
        rate -= settings.insurance_rate_discount
    if is_salary_client:
        rate -= settings.salary_rate_discount
    rate = max(Decimal("0"), rate)

    logger.debug("Rate: base=%s insurance=%s (-%s) salary=%s (-%s) -> %s",
                 settings.base_rate, is_insurance_enabled, settings.insurance_rate_discount,
                 is_salary_client, settings.salary_rate_discount, rate)
    return rate

#расчет суммы с добавлением страховки
def calculate_total_amount(amount: Decimal, is_insurance_enabled: bool) -> Decimal:
    total = round_to_kopecks(amount + settings.insurance_cost if is_insurance_enabled else amount)
    logger.debug("Total amount: requested=%s insurance=%s -> %s", amount, is_insurance_enabled, total)
    return total

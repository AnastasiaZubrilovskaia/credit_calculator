import calendar
import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from calculator.app.core.config import settings

logger = logging.getLogger(__name__)

CENT = Decimal("0.01")
ZERO = Decimal("0")

def _round_to_kopecks(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _add_months(source: date, months: int) -> date:
    month_index = source.month - 1 + months
    year = source.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

#подсчет размера ежемесячного платежа
def _calculate_annuity_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    monthly_rate = annual_rate / Decimal("1200")
    factor = (Decimal(1) + monthly_rate) ** months
    payment = _round_to_kopecks(principal * monthly_rate * factor / (factor - Decimal(1)))
    return payment

#построение графика платежей
def  _calculate_payment_schedule(principal: Decimal, annual_rate: Decimal, months: int,
                     start_date: date | None = None) -> tuple[Decimal, list[dict]]:
    start = start_date or date.today()
    monthly_rate = annual_rate / Decimal("1200")
    payment = _calculate_annuity_payment(principal, annual_rate, months)
    balance = _round_to_kopecks(principal)
    schedule = []
    for number in range(1, months + 1):
        interest = _round_to_kopecks(balance * monthly_rate) #проценты за месяц
        debt = _round_to_kopecks(payment - interest) #долг
        total = payment
        if number == months or debt >= balance:
            debt = balance
            total = _round_to_kopecks(debt + interest)
        balance = _round_to_kopecks(max(ZERO, balance - debt))
        row = {
            "number": number,
            "date": _add_months(start, number),
            "totalPayment": total,
            "interestPayment": interest,
            "debtPayment": debt,
            "remainingDebt": balance,
        }
        schedule.append(row)
    logger.info("Payment schedule built: %s payments", months)
    return payment, schedule


#ПСК = (Суммарные выплаты / Сумма кредита - 1) / Срок в годах * 100
def _calculate_psk(amount: Decimal, term: int, monthly_payment: Decimal,
                         insurance_cost: Decimal = ZERO) -> Decimal:

    total_payments = (monthly_payment * term) + insurance_cost
    term_years = Decimal(term) / Decimal("12")
    psk = (total_payments / amount - Decimal("1")) / term_years * Decimal("100")
    psk_result = psk.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    logger.info("PSK calculated: total_payments=%s, amount=%s -> psk=%s%%",
                total_payments, amount, psk_result)
    return psk_result

#подсчет итоговой ставки с учетом скидок (наличия страховки, зарплаты)
def _calculate_rate(is_insurance_enabled: bool, is_salary_client: bool) -> Decimal:
    rate = settings.base_rate
    if is_insurance_enabled:
        rate -= settings.insurance_rate_discount
    if is_salary_client:
        rate -= settings.salary_rate_discount
    rate = max(Decimal("0"), rate)

    logger.debug("Rate: base=%s insurance=%s salary=%s -> %s",
                 settings.base_rate, is_insurance_enabled, is_salary_client, rate)
    return rate


#расчет суммы с добавлением страховки
def _calculate_total_amount(term: int, monthly_payment: Decimal,
                            is_insurance_enabled: bool) -> Decimal:
    insurance_cost = settings.insurance_cost if is_insurance_enabled else ZERO
    total = (monthly_payment * term) + insurance_cost
    total = _round_to_kopecks(total)

    logger.debug("Total amount: monthly=%s term=%s insurance=%s -> %s",
                 monthly_payment, term, is_insurance_enabled, total)
    return total
import calendar
import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

CENT = Decimal("0.01")
ZERO = Decimal("0")

def round_to_kopecks(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def add_months(source: date, months: int) -> date:
    month_index = source.month - 1 + months
    year = source.year + month_index // 12
    month = month_index % 12 + 1
    day = min(source.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

#подсчет размера ежемесячного платежа
def annuity_payment(principal: Decimal, annual_rate: Decimal, months: int) -> Decimal:
    if months <= 0:
        raise ValueError("months must be positive")
    if principal <= 0:
        raise ValueError("principal must be positive")
    monthly_rate = annual_rate / Decimal("1200")
    if monthly_rate == 0:
        payment = round_to_kopecks(principal / months)
    else:
        factor = (Decimal(1) + monthly_rate) ** months
        payment = round_to_kopecks(principal * monthly_rate * factor / (factor - Decimal(1)))
    return payment

#построение графика платежей
def payment_schedule(principal: Decimal, annual_rate: Decimal, months: int,
                     start_date: date | None = None) -> tuple[Decimal, list[dict]]:
    start = start_date or date.today()
    monthly_rate = annual_rate / Decimal("1200")
    payment = annuity_payment(principal, annual_rate, months)
    balance = round_to_kopecks(principal)
    schedule = []
    for number in range(1, months + 1):
        interest = round_to_kopecks(balance * monthly_rate) #проценты за месяц
        debt = round_to_kopecks(payment - interest) #долг
        total = payment
        if number == months or debt >= balance:
            debt = balance
            total = round_to_kopecks(debt + interest)
        balance = round_to_kopecks(max(ZERO, balance - debt))
        row = {
            "number": number,
            "date": add_months(start, number),
            "totalPayment": total,
            "interestPayment": interest,
            "debtPayment": debt,
            "remainingDebt": balance,
        }
        schedule.append(row)
    total_interest = sum((row["interestPayment"] for row in schedule), ZERO)

    logger.info("Payment schedule built: %s payments from %s to %s, total interest=%s, last payment=%s",
        months, schedule[0]["date"], schedule[-1]["date"], total_interest, schedule[-1]["totalPayment"],
    )
    return payment, schedule


#ПСК = годовая ставка + (стоимость страховки / сумма кредита / срок в годах) * 100
def calculate_psk(principal: Decimal, annual_rate: Decimal, term_months: int,
                         insurance_cost: Decimal = ZERO) -> Decimal:
    if principal <= 0 or term_months <= 0:
        return ZERO
    term_years = Decimal(term_months) / Decimal("12")

    if insurance_cost > 0 and term_years > 0:
        insurance_annual_rate = (insurance_cost / principal) / term_years * Decimal("100")
    else:
        insurance_annual_rate = ZERO

    psk = annual_rate + insurance_annual_rate

    psk_result = psk.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    logger.info("Simple PSK calculated: base_rate=%s, insurance_rate=%s -> psk=%s",
                 annual_rate, insurance_annual_rate, psk_result)
    return psk_result
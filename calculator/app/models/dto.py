from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator

NAME_PATTERN = r"^[A-Za-zА-Яа-яЁё-]{2,30}$"
PASSPORT_SERIES_PATTERN = r"^\d{4}$"
PASSPORT_NUMBER_PATTERN = r"^\d{6}$"

class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={Decimal: str})


class BaseApplicantDto(ApiModel):
    amount: Decimal = Field(ge=200000,le=5000000, max_digits=12, decimal_places=2)
    term: int = Field(ge=6, le=360)
    first_name: str = Field(alias="firstName", pattern=NAME_PATTERN)
    last_name: str = Field(alias="lastName", pattern=NAME_PATTERN)
    middle_name: str | None = Field(default=None, alias="middleName", pattern=NAME_PATTERN)
    birthdate: date
    passport_series: str = Field(alias="passportSeries", pattern=PASSPORT_SERIES_PATTERN)
    passport_number: str = Field(alias="passportNumber", pattern=PASSPORT_NUMBER_PATTERN)

    @field_validator("birthdate")
    @classmethod
    def validate_age(cls, value: date) -> date:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))

        if age < 18:
            raise ValueError("Age must be at least 18 years old")
        if age > 65:
            raise ValueError("Age must be at most 65 years old")

        return value


#запрос на получение кредитных предложений
class LoanStatementRequestDto(BaseApplicantDto):
    email: EmailStr


#одно кредитное предложение
class LoanOfferDto(ApiModel):
    statement_id: UUID = Field(alias="statementId")
    requested_amount: Decimal = Field(alias="requestedAmount")
    total_amount: Decimal = Field(alias="totalAmount")
    term: int
    monthly_payment: Decimal = Field(alias="monthlyPayment")
    rate: Decimal
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")

#данные для скоринга (оценки кредитоспособности)
class ScoringDataDto(BaseApplicantDto):
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")


#данные одного элемента графика платежей
class PaymentScheduleElementDto(ApiModel):
    number: int
    date: date
    total_payment: Decimal = Field(alias="totalPayment")
    interest_payment: Decimal = Field(alias="interestPayment")
    debt_payment: Decimal = Field(alias="debtPayment")
    remaining_debt: Decimal = Field(alias="remainingDebt")


#полный расчет кредита
class CreditDto(ApiModel):
    amount: Decimal
    term: int
    monthly_payment: Decimal = Field(alias="monthlyPayment")
    rate: Decimal
    psk: Decimal
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")
    payment_schedule: list[PaymentScheduleElementDto] = Field(alias="paymentSchedule")

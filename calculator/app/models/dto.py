from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator

NAME_PATTERN = r"^[A-Za-zА-Яа-яЁё-]{2,30}$"

class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={Decimal: str})


class DataMixin(ApiModel):
    amount: Decimal = Field(ge=10000, max_digits=12, decimal_places=2)
    term: int = Field(ge=6, le=360)
    first_name: str = Field(alias="firstName", pattern=NAME_PATTERN)
    last_name: str = Field(alias="lastName", pattern=NAME_PATTERN)
    middle_name: str | None = Field(default=None, alias="middleName", pattern=NAME_PATTERN)
    birthdate: date
    passport_series: str = Field(alias="passportSeries", pattern=r"^\d{4}$")
    passport_number: str = Field(alias="passportNumber", pattern=r"^\d{6}$")

    @field_validator("birthdate")
    @classmethod
    def birthdate_not_future(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Birthdate must be in the past")
        return value


#запрос на получение кредитных предложений
class LoanStatementRequestDto(DataMixin):
    email: EmailStr


#одно кредитное предложение
class LoanOfferDto(ApiModel):
    statement_id: UUID = Field(alias="statementId")
    requested_amount: Decimal = Field(alias="requestedAmount", gt=0)
    total_amount: Decimal = Field(alias="totalAmount", gt=0)
    term: int = Field(ge=1, le=360)
    monthly_payment: Decimal = Field(alias="monthlyPayment", gt=0)
    rate: Decimal = Field(ge=0)
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")

#данные для скоринга (оценки кредитоспособности)
class ScoringDataDto(DataMixin):
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")


#данные одного элемента графика платежей
class PaymentScheduleElementDto(ApiModel):
    number: int = Field(ge=1)
    date: date
    total_payment: Decimal = Field(alias="totalPayment", ge=0)
    interest_payment: Decimal = Field(alias="interestPayment", ge=0)
    debt_payment: Decimal = Field(alias="debtPayment", ge=0)
    remaining_debt: Decimal = Field(alias="remainingDebt", ge=0)


#полный расчет кредита
class CreditDto(ApiModel):
    amount: Decimal = Field(gt=0)
    term: int = Field(ge=1, le=360)
    monthly_payment: Decimal = Field(alias="monthlyPayment", ge=0)
    rate: Decimal = Field(ge=0)
    psk: Decimal = Field(ge=0)
    is_insurance_enabled: bool = Field(alias="isInsuranceEnabled")
    is_salary_client: bool = Field(alias="isSalaryClient")
    payment_schedule: list[PaymentScheduleElementDto] = Field(alias="paymentSchedule")

    @model_validator(mode="after")
    def schedule_matches_term(self):
        if len(self.payment_schedule) != self.term:
            raise ValueError("Payment schedule length must equal loan term")
        return self
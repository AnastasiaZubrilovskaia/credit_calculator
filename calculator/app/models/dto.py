from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, json_encoders={Decimal: str})

#запрос на получение кредитных предложений
class LoanStatementRequestDto(ApiModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    term: int = Field(ge=1, le=360)
    first_name: str = Field(alias="firstName", min_length=1, max_length=50)
    last_name: str = Field(alias="lastName", min_length=1, max_length=50)
    middle_name: str | None = Field(default=None, alias="middleName", max_length=50)
    email: EmailStr
    birthdate: date
    passport_series: str = Field(alias="passportSeries", pattern=r"^\d{4}$")
    passport_number: str = Field(alias="passportNumber", pattern=r"^\d{6}$")

    @field_validator("birthdate")
    @classmethod
    def birthdate_not_future(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Birthdate must be in the past")
        return value


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
class ScoringDataDto(ApiModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    term: int = Field(ge=1, le=360)
    first_name: str = Field(alias="firstName", min_length=1, max_length=50)
    last_name: str = Field(alias="lastName", min_length=1, max_length=50)
    middle_name: str | None = Field(default=None, alias="middleName", max_length=50)
    birthdate: date
    passport_series: str = Field(alias="passwordSeries", pattern=r"^\d{4}$")
    passport_number: str = Field(alias="passwordNumber", pattern=r"^\d{6}$")
    is_insurance_enabled: bool = Field(alias="isInsuranceEnable")
    is_salary_client: bool = Field(alias="isSalaryClient")

    @field_validator("birthdate")
    @classmethod
    def birthdate_not_future(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Birthdate must be in the past")
        return value


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
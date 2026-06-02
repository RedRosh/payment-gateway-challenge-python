from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    Field,
    computed_field,
)
import datetime as dt
import re
from typing import Literal
from payment_gateway_api.models import Currency


class CardPayment(BaseModel):
    card_number: str
    expiry_month: int
    expiry_year: int
    currency: Currency
    amount: int = Field(ge=0)
    cvv: str

    @field_validator("card_number", mode="after")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        if not re.fullmatch(r"\d{14,19}", v):
            raise ValueError("Card number must be 14-19 numeric characters")
        return v

    @field_validator("expiry_month", mode="after")
    @classmethod
    def validate_expiry_month(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError("Expiry month must be between 1 and 12")
        return v

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        if not re.fullmatch(r"\d{3,4}", v):
            raise ValueError("CVV must be 3-4 numeric characters")
        return v

    @model_validator(mode="after")
    def validate_expiry_in_future(self) -> "CardPayment":
        today = dt.date.today()
        expiry = dt.date(self.expiry_year, self.expiry_month, 1)

        if expiry < dt.date(today.year, today.month, 1):
            raise ValueError("Card expiry date must be in the future")
        return self

    @computed_field
    @property
    def expiry_date(self) -> str:
        expiry = dt.date(self.expiry_year, self.expiry_month, 1)
        return expiry.strftime("%m/%Y")

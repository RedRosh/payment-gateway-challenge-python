import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    AUTHORIZED = "Authorized"
    DECLINED = "Declined"
    REJECTED = "Rejected"


# Only 3 currencies supported
Currency = Literal["USD", "EUR", "GBP"]


class PaymentResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: PaymentStatus
    last_four_card_digits: str
    expiry_month: int
    expiry_year: int
    currency: str
    amount: int

import requests
import logging

from returns.result import safe, ResultE
from returns.pipeline import flow
from returns.pointfree import bind

from payment_gateway_api.models import PaymentResult, PaymentStatus
from payment_gateway_api.serializers import CardPayment

logger = logging.getLogger(__name__)

BANK_URL = "http://localhost:8080"


@safe
def build_bank_payload(card_payment: CardPayment) -> dict:
    return {
        "card_number": card_payment.card_number,
        "expiry_date": card_payment.expiry_date,
        "currency": card_payment.currency,
        "amount": card_payment.amount,
        "cvv": card_payment.cvv,
    }


@safe
def send_to_bank(payload: dict) -> dict:
    response = requests.post(f"{BANK_URL}/payments", json=payload)
    response.raise_for_status()
    return {"payload": payload, "bank_response": response.json()}


@safe
def to_payment_result(ctx: dict) -> PaymentResult:
    payload = ctx["payload"]
    bank_response = ctx["bank_response"]

    status = (
        PaymentStatus.AUTHORIZED
        if bank_response.get("authorized")
        else PaymentStatus.DECLINED
    )

    return PaymentResult(
        status=status,
        last_four_card_digits=payload["card_number"][-4:],
        expiry_month=int(payload["expiry_date"].split("/")[0]),
        expiry_year=int(payload["expiry_date"].split("/")[1]),
        currency=payload["currency"],
        amount=payload["amount"],
    )


def process_payment(card_payment: CardPayment) -> ResultE[PaymentResult]:
    return flow(
        card_payment,
        build_bank_payload,
        bind(send_to_bank),
        bind(to_payment_result),
    )

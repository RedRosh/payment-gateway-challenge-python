import requests
import logging

from returns.result import Success, Failure, Result

from payment_gateway_api.models import PaymentResult, PaymentStatus
from payment_gateway_api.serializers import CardPayment

logger = logging.getLogger(__name__)

BANK_URL = "http://localhost:8080"


def build_bank_payload(card_payment: CardPayment) -> Result[dict, str]:
    payload = {
        "card_number": card_payment.card_number,
        "expiry_date": card_payment.expiry_date,
        "currency": card_payment.currency,
        "amount": card_payment.amount,
        "cvv": card_payment.cvv,
    }
    return Success(payload)


def send_to_bank(payload: dict) -> Result[dict, str]:
    try:
        response = requests.post(f"{BANK_URL}/payments", json=payload)
        response.raise_for_status()
        return Success({"payload": payload, "bank_response": response.json()})
    except Exception as e:
        logger.error(f"Bank request failed: {e}")
        return Failure(f"Bank unavailable: {e}")


def to_payment_result(ctx: dict) -> Result[PaymentResult, str]:
    payload = ctx["payload"]
    bank_response = ctx["bank_response"]

    status = (
        PaymentStatus.AUTHORIZED
        if bank_response.get("authorized")
        else PaymentStatus.DECLINED
    )

    result = PaymentResult(
        status=status,
        last_four_card_digits=payload["card_number"][-4:],
        expiry_month=int(payload["expiry_date"].split("/")[0]),
        expiry_year=int(payload["expiry_date"].split("/")[1]),
        currency=payload["currency"],
        amount=payload["amount"],
    )
    return Success(result)


def process_payment(card_payment: CardPayment) -> Result[PaymentResult, str]:
    return (
        build_bank_payload(card_payment)
        .bind(send_to_bank)
        .bind(to_payment_result)
    )

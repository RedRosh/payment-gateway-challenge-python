from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from returns.pipeline import is_successful

from payment_gateway_api.serializers import CardPayment
from payment_gateway_api.bank_client import process_payment
from payment_gateway_api.repository import payment_repository
from payment_gateway_api.models import PaymentStatus

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"status": PaymentStatus.REJECTED.value},
    )


@app.post("/payments")
async def post_payment(card_payment: CardPayment):
    result = process_payment(card_payment)

    match result:
        case _ if is_successful(result):
            payment = result.unwrap()
            payment_repository.save(payment)
            return payment
        case _:
            return JSONResponse(
                status_code=400,
                content={"status": PaymentStatus.REJECTED.value},
            )


@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    payment = payment_repository.get(payment_id)
    if payment is None:
        return JSONResponse(status_code=404, content={"error": "Payment not found"})
    return payment

from unittest.mock import patch
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient
from returns.result import Success

from payment_gateway_api.app import app
from payment_gateway_api.models import PaymentResult, PaymentStatus


client = TestClient(app)

_future_date = date.today() + relativedelta(months=+3)


def _valid_payment_request():
    return {
        "card_number": "2222405343248877",
        "expiry_month": _future_date.month,
        "expiry_year": _future_date.year,
        "currency": "GBP",
        "amount": 100,
        "cvv": "123",
    }


class TestGetPayment:
    @patch("payment_gateway_api.app.process_payment")
    def test_retrieve_existing_payment(self, mock_process):
        mock_process.return_value = Success(
            PaymentResult(
                status=PaymentStatus.AUTHORIZED,
                last_four_card_digits="8877",
                expiry_month=_future_date.month,
                expiry_year=_future_date.year,
                currency="GBP",
                amount=100,
            )
        )

        post_response = client.post("/payments", json=_valid_payment_request())
        payment_id = post_response.json()["id"]

        get_response = client.get(f"/payments/{payment_id}")

        assert get_response.status_code == 200
        assert get_response.json()["id"] == payment_id
        assert get_response.json()["status"] == "Authorized"

    def test_retrieve_nonexistent_payment(self):
        response = client.get("/payments/nonexistent-id")

        assert response.status_code == 404

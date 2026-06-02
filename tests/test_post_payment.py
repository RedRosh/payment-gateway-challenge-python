from unittest.mock import patch
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi.testclient import TestClient
from returns.result import Success, Failure

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


class TestProcessPaymentAuthorized:
    @patch("payment_gateway_api.app.process_payment")
    def test_returns_200(self, mock_process):
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

        response = client.post("/payments", json=_valid_payment_request())

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "Authorized"
        assert body["last_four_card_digits"] == "8877"
        assert body["expiry_month"] == _future_date.month
        assert body["expiry_year"] == _future_date.year
        assert body["currency"] == "GBP"
        assert body["amount"] == 100
        assert "id" in body


class TestProcessPaymentDeclined:
    @patch("payment_gateway_api.app.process_payment")
    def test_returns_200_with_declined_status(self, mock_process):
        mock_process.return_value = Success(
            PaymentResult(
                status=PaymentStatus.DECLINED,
                last_four_card_digits="8872",
                expiry_month=_future_date.month,
                expiry_year=_future_date.year,
                currency="GBP",
                amount=100,
            )
        )

        request = _valid_payment_request()
        request["card_number"] = "2222405343248872"
        response = client.post("/payments", json=request)

        assert response.status_code == 200
        assert response.json()["status"] == "Declined"


class TestProcessPaymentRejected:
    def test_invalid_card_number(self):
        request = _valid_payment_request()
        request["card_number"] = "abc"

        response = client.post("/payments", json=request)

        assert response.status_code == 400
        assert response.json()["status"] == "Rejected"

    def test_missing_cvv(self):
        request = _valid_payment_request()
        del request["cvv"]

        response = client.post("/payments", json=request)

        assert response.status_code == 400
        assert response.json()["status"] == "Rejected"

    def test_expired_card(self):
        request = _valid_payment_request()
        request["expiry_month"] = 1
        request["expiry_year"] = 2020

        response = client.post("/payments", json=request)

        assert response.status_code == 400
        assert response.json()["status"] == "Rejected"

    def test_invalid_currency(self):
        request = _valid_payment_request()
        request["currency"] = "XYZ"

        response = client.post("/payments", json=request)

        assert response.status_code == 400
        assert response.json()["status"] == "Rejected"

    @patch("payment_gateway_api.app.process_payment")
    def test_bank_failure_returns_rejected(self, mock_process):
        mock_process.return_value = Failure("Bank unavailable")

        response = client.post("/payments", json=_valid_payment_request())

        assert response.status_code == 400
        assert response.json()["status"] == "Rejected"

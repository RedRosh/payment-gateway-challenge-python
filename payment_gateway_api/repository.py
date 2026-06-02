from payment_gateway_api.models import PaymentResult


class PaymentRepository:
    def __init__(self):
        self._store: dict[str, PaymentResult] = {}

    def save(self, payment: PaymentResult) -> PaymentResult:
        self._store[payment.id] = payment
        return payment

    def get(self, payment_id: str) -> PaymentResult | None:
        return self._store.get(payment_id)


# Single shared instance
payment_repository = PaymentRepository()

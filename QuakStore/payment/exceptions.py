from django.utils.translation import gettext_lazy as _

class PaymentFailure(Exception):
    def __init__(self, message = None, *args: object) -> None:
        message = message or _("Payment failed. Try Again or use a different method.")
        self.message = message
        super().__init__(message, *args)
        
class CardFailure(PaymentFailure):
    def __init__(self, message = None, *args: object) -> None:
        super().__init__(message or _("Card Payment Failed. Try Again or use a different method."), *args)
        
class InsufficientFunds(PaymentFailure):
    def __init__(self, message=None, *args: object) -> None:
        super().__init__(message or _("Insufficient Funds."), *args)
        
class DuplicatedPaymentError(PaymentFailure):
    def __init__(self, message=None, *args: object) -> None:
        super().__init__(message or _("Duplicated payment."), *args)
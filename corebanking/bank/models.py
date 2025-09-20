from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL

class Account(models.Model):
    Account_type = (
        ("savings" ,"Savings"),
        ("current" ,"Current"),
    )
    id= models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    account_number = models.CharField(max_length=12, unique=True)
    account_type = models.CharField(choices=Account_type, max_length=10)
    balance = models.DecimalField(max_digits=12,decimal_places=2, default=0.00)
    status = models.CharField(
    max_length=10,
    choices=[("active", "Active"), ("inactive", "Inactive"), ("suspended", "Suspended")],
    default="active"
)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.account_number}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, db_index=True)
    account = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name="transactions"
    )
    destination_account = models.ForeignKey(
        "Account",
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        null=True,
        blank=True,
        help_text="Only required for transfers",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    is_credit = models.BooleanField()
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.type == "transfer" and self.destination_account:
            return f"Transfer {self.amount} from {self.account.account_number} to {self.destination_account.account_number}"
        return f"{self.type.capitalize()} {self.amount} on {self.account.account_number} ({self.status})"


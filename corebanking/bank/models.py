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
    Transaction_type = (
        ("deposit","Deposit"),
        ("withdrawal","Withdrawal"),
        ("transfer", "Transfer"),
    )
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transaction")
    transaction_type= models.CharField(choices=Transaction_type, max_length=12)
    destination_account= models.ForeignKey(
        Account, on_delete=models.CASCADE,
        related_name="incoming_transaction", null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True, max_length= 50)
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        if self.destination_account:
            return f"Transfer from {self.account.user.email} - {self.account.account_number} to {self.destination_account.user.email} - {self.destination_account.account_number}"
        return f"{self.transaction_type.capitalize()} {self.amount} on {self.account.account_number}"

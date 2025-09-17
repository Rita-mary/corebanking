from django.contrib import admin
from .models import Account, Transaction

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_number", "account_type", "balance","status", "created_at")
    search_fields = ("account_number", "user__email", "user__full_name")
    list_filter = ("account_type","status",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "destination_account", "transaction_type", "amount", "created_at")
    search_fields = ("account__account_number", "destination_account__account_number", "account__user__email")
    list_filter = ("transaction_type",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

from rest_framework import serializers
from .models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = Account
        fields = ["id", "user", "account_number","account_type" ,"balance", "created_at"]
        read_only_fields = ["id", "balance", "account_number", "created_at"]
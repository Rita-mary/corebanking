from rest_framework import serializers
from .models import Account, Transaction
from decimal import Decimal

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = Account
        fields = ["id", "user", "account_number","account_type" ,"status","balance", "created_at"]
        read_only_fields = ["id", "balance", "account_number", "created_at"]

class TransferSerializer(serializers.Serializer):
    sender_account = serializers.CharField(allow_blank = False, required = True)
    destination_account = serializers.CharField(allow_blank = False, required = True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(allow_blank = True, required = False)

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError({"error": "Amount must be greater than zero."})
        return value
    def validate(self,attrs):
        if attrs['sender_account'] == attrs['destination_account']:
            raise serializers.ValidationError({"error": "Sender and Destination accounts must be different."})
        # check that accounts are available
        try:
            sender = Account.objects.get(account_number= attrs['sender_account'])
        except Account.DoesNotExist:
            raise serializers.ValidationError({"error": "Sender Account does not exist"})
        try:
            dest = Account.objects.get(account_number= attrs['destination_account'])
        except Account.DoesNotExist:
            raise serializers.ValidationError({"error": "Destination Account does not exist"})
        
        if sender.status != 'active':
            raise serializers.ValidationError({"error": "The Sender's account is not active"})
        if dest.status != 'active':
            raise serializers.ValidationError({"error": "The Receivers's account is not active"})
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            raise serializers.ValidationError("Authentication required.")
        if sender.user != request.user:
            raise serializers.ValidationError({"sender_account": "Sender account does not belong to the authenticated user."})
        
        #Attach the sender and destination attributes for use in the view 
        attrs['_sender_obj'] = sender
        attrs['_destination_obj'] = dest

        return attrs
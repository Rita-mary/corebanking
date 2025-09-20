from rest_framework import generics, permissions, status
from .models import Account
from .serializers import AccountSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import generate_account_number
from drf_spectacular.utils import extend_schema
from django.db import transaction as db_transaction
from .models import Transaction
from .serializers import TransferSerializer
from .utils import generate_reference

@extend_schema(
        tags=["Account"],
        summary="Get or List User Account",
        description="Get methods gets list of all the accounts by the same user ,while Create method creates a new object."
    )
class AccountListCreateView(generics.ListCreateAPIView):
    """Handles listing all accounts for the logged-in user and creating a new one"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        # Only return accounts owned by the current user
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically generate account number + attach user
        account_number = generate_account_number()
        serializer.save(user=self.request.user, account_number=account_number)

@extend_schema(
        tags=["Account"],
        summary="Retrieve ,Update or Delete User Account",
        description="Depending on the method choice, the user Acount either gets retrieved, updated or deleted."
    )
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Handles retrieving, updating, and deleting a single account"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        # Restrict detail view to the logged-in user's accounts
        return Account.objects.filter(user=self.request.user)
    
class TransferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Transaction"],
        summary="Transfer to another account",
        description="Transfer money from one account to the other."
    )
    def post(self, request, *args, **kwargs):
        """
        Perform an internal transfer between two accounts (double-entry).
        Expects JSON:
        {
          "sender_account": "2280000002",
          "destination_account": "2280000001",
          "amount": "5000.00",
          "description": "Payment for GoTv"
        }
        """
        serializer = TransferSerializer(data = request.data, context = {"request": request})
        serializer.is_valid(raise_exception = True)
        data = serializer.validated_data

        sender = data['_sender_obj']
        dest = data['_destination_obj']
        amount= data['amount']
        description = data.get('description', '')
        try:
            # Lock both accounts in a deterministic order to avoid deadlocks
             # Order by id ensures both concurrent transfers lock in same order.
            with db_transaction.atomic():
                if str(sender.id)< str(dest.id):
                    sender = sender.__class__.objects.select_for_update().get(id = sender.id)
                    dest = dest.__class__.objects.select_for_update().get(id = dest.id)
                else:
                    dest = dest.__class__.objects.select_for_update.get(id = dest.id)
                    sender = sender.__class__.objects.select_for_update.get(id = sender.id)

                if sender.status != 'active' or dest.status != 'active':
                    return Response({"detail": "One of the accounts is not active."}, status.HTTP_400_BAD_REQUEST)
                if sender.balance < amount:
                    ref_fail = generate_reference()
                    Transaction.objects.create(
                    reference=ref_fail,
                    account=sender,
                    destination_account=dest,
                    amount=amount,
                    type="transfer",
                    is_credit=False,
                    description=(description or "Transfer attempted - insufficient funds"),
                    status="failed",
                    )
                    return Response({'error':'Insufficient  funds'}, status.HTTP_400_BAD_REQUEST)
                #if all checks are correct
                sender.balance -= amount
                dest.balance += amount

                sender.save()
                dest.save()

                ref = generate_reference()
                debit = Transaction.objects.create(
                    reference=ref,
                    account=sender,
                    destination_account=dest,
                    amount=amount,
                    type="transfer",
                    is_credit=False,
                    description=description or f"Transfer to {dest.account_number}",
                    status="success",
                )

                credit = Transaction.objects.create(
                    reference=ref,
                    account=dest,
                    destination_account=sender,
                    amount=amount,
                    type="transfer",
                    is_credit=True,
                    description=description or f"Transfer from {sender.account_number}",
                    status="success",
                )

                return Response({
                    "message": "Transfer successful",
                    "reference": ref,
                    "debit_id": str(debit.id),
                    "credit_id": str(credit.id),
                    "amount": str(amount),
                    "from_account": str(sender.account_number),
                    "to_account": str(dest.account_number),
                }, status=status.HTTP_200_OK)

                
        except Exception as e:
            return Response({"detail": "Transfer failed", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



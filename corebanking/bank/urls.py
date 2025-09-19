from django.urls import path
from .views import AccountListCreateView, AccountDetailView , TransferView

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path("transactions/transfer/", TransferView.as_view(), name="transfer"),
]

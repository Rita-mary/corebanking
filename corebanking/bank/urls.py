from django.urls import path
from .views import AccountCreateView, AccountListView, AccountDetailView

urlpatterns = [
    path('account_create/', AccountCreateView.as_view(), name='account_create'),
    path("accounts/", AccountListView.as_view(), name="account-list"),
    path("accounts/<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
]

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Account

User = get_user_model()


class AccountAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            full_name="Test User",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_create_account(self):
        url = reverse('account-list-create')
        data = {"account_type": "savings"}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        obj = Account.objects.filter(user=self.user).first()
        self.assertIsNotNone(obj)
        self.assertEqual(obj.account_type, "savings")
        self.assertTrue(hasattr(obj, 'account_number'))
        self.assertTrue(len(obj.account_number) == 10)

    def test_list_accounts(self):
        ac1 = Account.objects.create(
            user=self.user,
            account_number="2280000001",
            account_type="savings",
            balance=0
        )
        ac2 = Account.objects.create(
            user=self.user,
            account_number="2280000002",
            account_type="savings",
            balance=0
        )
        other_user = User.objects.create_user(
            email="other@example.com",
            full_name="Other",
            password="pass123"
        )
        Account.objects.create(
            user=other_user,
            account_number="2280000003",
            account_type="current",
            balance=0
        )

        url = reverse('account-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # only self.user’s accounts
        created_numbers = {item["account_number"] for item in response.data}
        self.assertIn(ac1.account_number, created_numbers)
        self.assertIn(ac2.account_number, created_numbers)

    def test_view_account(self):
        ac = Account.objects.create(
            user=self.user,
            account_number="2280000004",
            account_type="savings",
            balance=119.27
        )

        url = reverse('account-detail', kwargs={'pk': str(ac.id)})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_number"], ac.account_number)
        self.assertEqual(response.data["balance"], str(ac.balance))

    def test_update_account(self):
        ac = Account.objects.create(
            user=self.user,
            account_number="2280000005",
            account_type="savings",
            balance=200.00
        )

        url = reverse('account-detail', kwargs={'pk': str(ac.id)})
        data = {"account_type": "current"}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ac.refresh_from_db()
        self.assertEqual(ac.account_type, "current")

    def test_delete_account(self):
        ac = Account.objects.create(
            user=self.user,
            account_number="2280000006",
            account_type="savings",
            balance=50.00
        )

        url = reverse('account-detail', kwargs={'pk': str(ac.id)})
        response = self.client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Account.objects.filter(id=ac.id).exists())

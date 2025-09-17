from.models import Account

def generate_account_number():
    prefix = "228"
    last_account = Account.objects.order_by("-id").first()
    if last_account:
        new_account_number = int(last_account.account_number)+ 1
        new_account_number = str(new_account_number)
    else:
        new_account_number = prefix + "0"*7
    return new_account_number
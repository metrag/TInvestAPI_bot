import os

from datetime import datetime
from decimal import Decimal

from tinkoff.invest import MoneyValue
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TINKOFF_TOKEN")

# закинуть деньги на песочницу - руб
def add_money_sandbox(cl, acc_id, money, currency="rub"):
    money = decimal_to_quotation(Decimal(money))
    return cl.sandbox.sandbox_pay_in(
        account_id=acc_id,
        amount=MoneyValue(units=money.units, nano=money.nano, currency=currency),
    )
    """
        MoneyValue -Денежная сумма в определенной валюте
            currency (string) -	Строковый ISO-код валюты
            units	 (int64)  -	Целая часть суммы, может быть отрицательным числом
            nano	 (int32)  -	Дробная часть суммы, может быть отрицательным числом
    """

def get_money_sandbox(cl, acc_id):
    return cl.operations.get_portfolio(account_id=acc_id).positions[0].quantity
def main():
 
    with SandboxClient(TOKEN) as cl:
        # информация по всем аккаунатм песочницы
        sandbox_accounts = cl.users.get_accounts().accounts

        print(f"Num accs: {len(sandbox_accounts)}") # количество аккаунтов
        for acc in sandbox_accounts:
            info = f"id={acc.id}\ntype={acc.type}\nstatus={acc.status}\nopened_date={acc.opened_date}\naccess_level={acc.access_level})"
            print(info)

        acc_id = sandbox_accounts[0].id

        # закрыть все (или один аккаунт)
        # for acc in sandbox_accounts:
        #     cl.sandbox.close_sandbox_account(account_id=acc.id)
        
        # открыть аккаунт
        # sandbox_account = cl.sandbox.open_sandbox_account()


        # завести деньги
        add_money_sandbox(cl=cl, acc_id=acc_id, money=1_000_000)

        # получение портфеля по счёту (см. PortfolioResponse)
        r = cl.operations.get_portfolio(account_id=acc_id)
        print(r)

        # получить стоимость портфеля
        cur_money = get_money_sandbox(cl=cl, acc_id=acc_id)
        print(cur_money.units)
        
if __name__ == "__main__":
    main()
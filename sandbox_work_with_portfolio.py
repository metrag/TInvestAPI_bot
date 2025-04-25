import os

from datetime import datetime
from decimal import Decimal

from tinkoff.invest import MoneyValue, Quotation, PortfolioPosition, RequestError
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from dotenv import load_dotenv

import pandas as pd
pd.set_option('display.max_rows', None)  # Показать все строки
pd.set_option('display.max_columns', None)  # Показать все колонки

load_dotenv()
TOKEN = os.getenv("TINKOFF_TOKEN")
ACC_ID=os.getenv("SANDBOX_ACC_ID")

positions_params = ['figi', 'instrument_type', 'quantity', 'average_position_price', 'expected_yield', 'average_position_price_pt', 'current_price', 'average_position_price_fifo', 'quantity_lots']
# пополнение баланса на песочницу - руб
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
            nano	 (int32)  -	Дробная часть суммы, может быть отрицательным числом (10^-9)
    """

def cast_quantity(q: Quotation):
    return q.units + q.nano / 1e9
 
def cast_money(m: MoneyValue):
    return m.units + m.nano / 1e9

def portfolio_pose_todict(p : PortfolioPosition):
    d = {
        'figi': p.figi,
        'quantity': cast_quantity(p.quantity),
        'expected_yield': cast_quantity(p.expected_yield),
        'instrument_type': p.instrument_type,
        'average_buy_price': cast_money(p.average_position_price),
        'currency': p.average_position_price.currency,
        'nkd' : cast_money(p.current_nkd)
    }
    d['sell_sum'] = d['average_buy_price']*d['quantity']+d['expected_yield']+d['nkd']*d['quantity']
    d['comission'] = d['sell_sum']*0.003
    d['tax'] = d['expected_yield']*0.013 if d['expected_yield'] > 0 else 0 # налоги, если положительная прибыль

    '''
        лимит количества запросов -  100
        average_position_price - средняя цена лота в позиции (средне арифем за с дня покупки)
        expected_yield - текущая рассчитанная доходность (последнняя закрытая цена по бумаге - average_position_price), доход в терминале
    '''
    
def main(): 
    try:
        with SandboxClient(TOKEN) as cl:
            sandbox_accounts = cl.users.get_accounts().accounts

            acc = None
            acc_id = ACC_ID
            for tempAcc in sandbox_accounts:
                if tempAcc.id == ACC_ID:
                    acc = tempAcc

            info_acc = f"id={acc.id}\ntype={acc.type}\nstatus={acc.status}\nopened_date={acc.opened_date}\naccess_level={acc.access_level})"
            # print(info_acc)
            info_portfolio = cl.operations.get_portfolio(account_id=acc_id)
            # print(info_portfolio)  
            dfPortfolio = pd.DataFrame([portfolio_pose_todict(p) for p in info_portfolio.positions])
            print(dfPortfolio)
       
    except RequestError as e:
        print(str(e))
        
if __name__ == "__main__":
    main()
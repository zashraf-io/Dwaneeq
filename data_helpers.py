"This file contains the functions doing data handling, currency calculations, etc"
from __future__ import annotations
import db
import config
import datetime


def from_to(amount, from_currency, to_currency):
    if amount == 0.0:
        return 0.0

    if from_currency == to_currency:
        return round(amount, 2)

    if to_currency == 'EGP':
        return round(amount * db.get_currency_rate(from_currency), 2)

    if from_currency == 'EGP':
        return round(amount / db.get_currency_rate(to_currency), 2)

    return round((amount * db.get_currency_rate(from_currency) / db.get_currency_rate(to_currency)), 2)

def get_total_budget(user_id, budget_id="latest") -> float | str:

    if budget_id == "latest" and db.isfound_budget(user_id):
        budget_id = db.get_latest_budget_info(user_id)[0]
    else:
        return config.choosed_lang["not_set"]

    budget = db.get_budget(budget_id)
    total_budget = budget[0][0]
    currency = budget[0][2]

    if currency == config.currency:
        return total_budget

    return from_to(total_budget, currency, config.currency)

def calc_amount(user_id, type, category_id=None, month: str="now"):
    "month can be ['now', 'all'] or date formated as 'YYYY-mm'"
    if month == "now":
        month = datetime.datetime.now().strftime(r"%Y-%m")

    if category_id == "all" or category_id == "":
        category_id = None

    amounts = db.get_amount(user_id, type, category_id, month)
    sum = amounts[0]
    if sum == None:
        sum = 0.0

    if amounts[1] == []:
        return from_to(sum, 'EGP', config.currency)

    for amount, currency in amounts[1]:
        sum += from_to(amount, currency, 'EGP')

    return from_to(sum, 'EGP', config.currency)


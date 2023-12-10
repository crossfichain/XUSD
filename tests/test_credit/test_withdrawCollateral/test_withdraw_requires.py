import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time


def test_position_existence(credit, xusd):
    not_user = accounts[0]

    amount = Wei("1 ether")

    with brownie.reverts("Credit: Position doesn't exist"):
        credit.withdrawCollateralFromPosition(amount, {"from": not_user})


def test_amount_in_greater_collateral_in_position(credit, xusd):
    user = accounts[0]

    amount = Wei("1 ether")
    amount_XUSD = 10*10**18  # 10$

    credit.takeLoan(amount_XUSD, {"from": user, "value": amount})

    assert xusd.balanceOf(user) == amount_XUSD

    with brownie.reverts("Credit: Incorrect amount to withdraw"):
        credit.withdrawCollateralFromPosition(amount, {"from": user})


def test_position_will_be_healthy_after_withdraw_1(credit, xusd):
    user = accounts[0]

    amount_collateral = Wei("1 ether")
    amount_XUSD = 100*10**18  # 100$

    amount_withdraw = Wei("0.9 ether")

    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})

    assert xusd.balanceOf(user) == amount_XUSD

    with brownie.reverts("Credit: Incorrect amount to withdraw"):
        credit.withdrawCollateralFromPosition(amount_withdraw, {"from": user})


def test_position_will_be_healthy_after_withdraw_2(credit, xusd):
    user = accounts[0]

    amount_collateral = Wei("1 ether")
    amount_XUSD = 100*10**18  # 100$

    amount_withdraw = Wei("0.5 ether")

    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})

    balance_before = user.balance()

    assert xusd.balanceOf(user) == amount_XUSD

    # with brownie.reverts("Credit: Incorrect amount to withdraw"):
    credit.withdrawCollateralFromPosition(amount_withdraw, {"from": user})

    assert user.balance() == balance_before + amount_withdraw


def test_position_will_be_healthy_after_withdraw_3(credit, xusd):
    user = accounts[0]

    ratio = 3

    decimals_price = 8

    amount_collateral = Wei("1 ether")
    amount_XUSD = 100*10**18  # 100$

    price_collateral = credit.getPriceFeeds()

    amount_withdraw_critical = amount_collateral - ratio * \
        amount_XUSD*10**decimals_price/price_collateral - 1000

    print("amount_withdraw_critical =====", amount_withdraw_critical/10**18)
    print("price_collateral ========", price_collateral)

    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})
    balance_before = user.balance()
    assert xusd.balanceOf(user) == amount_XUSD

    # with brownie.reverts("Credit: Incorrect amount to withdraw"):
    credit.withdrawCollateralFromPosition(
        amount_withdraw_critical, {"from": user})

    assert user.balance() == balance_before + amount_withdraw_critical


def test_position_will_be_healthy_after_withdraw_4(credit, xusd):
    user = accounts[0]

    ratio = 3

    decimals_price = 8

    amount_collateral = Wei("1 ether")
    amount_XUSD = 100*10**18  # 100$

    price_collateral = credit.getPriceFeeds()

    amount_withdraw_critical = 1000 + amount_collateral - \
        ratio*amount_XUSD*10**decimals_price/price_collateral

    print("amount_withdraw_critical =====", amount_withdraw_critical/10**18)
    print("price_collateral ========", price_collateral)

    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})

    assert xusd.balanceOf(user) == amount_XUSD

    with brownie.reverts("Credit: Incorrect amount to withdraw"):
        credit.withdrawCollateralFromPosition(
            amount_withdraw_critical, {"from": user})

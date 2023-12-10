import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest


def test_liquidation_price(credit, accounts):

    amountCollateral = int(2e18)
    amountXUSd = int(500e18)

    decimals_oracle = 8

    right_answer = 500*10**decimals_oracle

    response_from_contract = credit.calculateLiquidationPrice(
        amountXUSd, amountCollateral).return_value
    # print("Response", response_from_contract.return_value)
    # print("Function answer", response_from_contract["value"])
    assert response_from_contract == right_answer

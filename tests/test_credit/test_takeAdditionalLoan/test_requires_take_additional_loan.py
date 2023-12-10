import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
import time
import json
from web3 import Web3
from brownie import chain
from brownie import Wei


def test_amount_to_mint_greater_than_zero(credit, xusd):
    user = accounts[0]

    initial_amount_xusd = 100*10**18

    collateral = Wei("1 ether")

    amount_to_add = 0

    credit.takeLoan(initial_amount_xusd, {"from": user, "value": collateral})

    assert xusd.balanceOf(user) == initial_amount_xusd

    with brownie.reverts("Credit: incorrect amount to mint"):
        credit.takeAdditionalLoan(amount_to_add, {"from" : user})


def test_existence_of_position(credit, xusd):
    user = accounts[0]

    collateral = Wei("1 ether")

    amount_to_mint = 100*10**18

    with brownie.reverts("Credit: Position doesn't exist"):
        credit.takeAdditionalLoan(amount_to_mint, {"from" : user})

def test_is_enough_XFI_to_mint(credit, xusd):
    user = accounts[0]

    initial_amount_xusd = 100*10**18

    collateral = Wei("1 ether")

    amount_to_add = 1000*10**18

    credit.takeLoan(initial_amount_xusd, {"from": user, "value": collateral})

    assert xusd.balanceOf(user) == initial_amount_xusd

    with brownie.reverts("Credit: Not enough XFI to take more XUSD"):
        credit.takeAdditionalLoan(amount_to_add, {"from" : user})
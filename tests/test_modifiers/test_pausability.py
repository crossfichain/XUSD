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


def test_pause(credit, xusd):
    owner = accounts[0]

    user = accounts[1]

    amount_to_mint = 100 * 10**18
    amount_in_XFI = Wei("1 ether")

    credit.pause({"from" : owner})

    with brownie.reverts("Pausable: paused"):
        credit.takeLoan(amount_to_mint, {"from" : user, "value" : amount_in_XFI})


def test_unpause(credit, xusd):
    owner = accounts[0]

    user = accounts[1]

    amount_to_mint = 100 * 10**18
    amount_in_XFI = Wei("1 ether")

    credit.pause({"from" : owner})

    with brownie.reverts("Pausable: paused"):
        credit.takeLoan(amount_to_mint, {"from" : user, "value" : amount_in_XFI})

    credit.unpause({"from" : owner})

    credit.takeLoan(amount_to_mint, {"from" : user, "value" : amount_in_XFI})

    assert xusd.balanceOf(user) == amount_to_mint


def test_ownability_pause(credit, xusd):
    not_owner = accounts[1]

    with brownie.reverts("Ownable: caller is not the owner"):
        credit.pause({"from": not_owner})


def test_ownability_unpause(credit, xusd):
    not_owner = accounts[1]

    with brownie.reverts("Ownable: caller is not the owner"):

        credit.unpause({"from": not_owner})

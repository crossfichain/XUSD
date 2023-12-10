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


# testing that we are minting tokens to user
def test_take_loan(credit, xusd, accounts):
    sender = accounts[1]
    amount_to_mint = 100 * 10 ** 18
    amount_XFI_to_send = Wei("1 ether")

    credit.takeLoan(amount_to_mint, {
                    "from": sender, "value": amount_XFI_to_send})

    assert xusd.balanceOf(sender) == amount_to_mint


# # testing that if user doesn't have enough XFi so we don't mint XUSd for user
def test_not_enough_XFI(credit, xusd, accounts):
    sender = accounts[1]
    amount_to_mint = 100 * 10 ** 18

    ratio = 3
    price_collateral = credit.getPriceFeeds()
    price_collateral /= 10**8

    # this amount will never be valid
    amount_XFI_to_send = 0.99*ratio*amount_to_mint/(price_collateral)
    amount_XFI_to_send = Wei(amount_XFI_to_send)

    # print("amount_XFI_to_send = ", amount_XFI_to_send)

    with brownie.reverts("Credit: Not enough XFI to take a loan"):

        credit.takeLoan(amount_to_mint, {
            "from": sender, "value": amount_XFI_to_send})

    assert xusd.balanceOf(sender) == 0


def test_enough_XFI_to_mint(credit, xusd, accounts):
    sender = accounts[1]
    amount_to_mint = 100 * 10 ** 18

    ratio = 3
    price_collateral = credit.getPriceFeeds()
    price_collateral /= 10**8

    # this amount will always be valid
    amount_XFI_to_send = 1.01*ratio*amount_to_mint/(price_collateral)
    amount_XFI_to_send = Wei(amount_XFI_to_send)

    credit.takeLoan(amount_to_mint, {
        "from": sender, "value": amount_XFI_to_send})

    assert xusd.balanceOf(sender) == amount_to_mint


def test_that_user_can_hold_just_one_credit(credit, xusd, accounts):

    sender = accounts[1]
    amount_to_mint = 100 * 10 ** 18
    amount_XFI_to_send = Wei("1 ether")

    credit.takeLoan(amount_to_mint, {
                    "from": sender, "value": amount_XFI_to_send})

    with brownie.reverts("Credit: User already has credit position"):
        credit.takeLoan(amount_to_mint, {
            "from": sender, "value": amount_XFI_to_send})


def test_zero_amount_out(credit, xusd):
    sender = accounts[1]
    amount_to_mint = 0
    amount_XFI_to_send = Wei("1 ether")

    with brownie.reverts("Credit: Body of credit must be greater than 1 XUSD"):
        credit.takeLoan(amount_to_mint, {
            "from": sender, "value": amount_XFI_to_send})


def test_one_wei_amount_out(credit, xusd):

    sender = accounts[1]

    amount_to_mint = 1

    amount_XFI_to_send = 5

    with brownie.reverts("Credit: Body of credit must be greater than 1 XUSD"):
        credit.takeLoan(amount_to_mint, {
            "from": sender, "value": amount_XFI_to_send})

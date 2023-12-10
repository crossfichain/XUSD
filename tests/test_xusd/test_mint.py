import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD


def test_mint(credit, xusd, accounts):
    owner = credit
    amount = 100

    assert xusd.balanceOf(owner.address) == 0

    xusd.mint(owner, amount, {"from": owner})

    assert xusd.balanceOf(owner.address) == amount


def test_mint_ownable(credit, xusd, accounts):
    not_owner = accounts[1]

    amount = 100

    assert xusd.owner() != not_owner

    with brownie.reverts("Ownable: caller is not the owner"):
        xusd.mint(not_owner, amount, {"from": not_owner})

    assert xusd.balanceOf(not_owner.address) == 0

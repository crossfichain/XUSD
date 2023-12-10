import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD


def test_burn(credit, xusd, accounts):
    owner = credit
    amount_to_mint = 100
    amount_to_burn = 20
    receiver = accounts[1]

    xusd.mint(receiver, amount_to_mint, {"from": owner})

    assert xusd.balanceOf(receiver.address) == amount_to_mint

    xusd.burn(receiver, amount_to_burn, {"from": owner})

    assert xusd.balanceOf(
        receiver.address) == amount_to_mint - amount_to_burn


def test_burn_ownable(credit, xusd, accounts):
    owner = credit
    amount_to_mint = 100

    not_owner = accounts[1]

    xusd.mint(owner.address, amount_to_mint, {"from": owner})

    with brownie.reverts("Ownable: caller is not the owner"):
        xusd.burn(owner, amount_to_mint, {"from": not_owner})

    print(xusd.balanceOf(owner.address) == amount_to_mint)

    assert xusd.balanceOf(owner.address) == amount_to_mint

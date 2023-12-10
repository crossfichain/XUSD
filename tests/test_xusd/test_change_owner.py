import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD


def test_mint_change_owner():
    deployer = accounts[0]
    owner = accounts[1]
    # print(owner)

    xusd = XUSD.deploy(owner, {"from": deployer})
    # print(xusd.owner())
    assert xusd.owner() == owner

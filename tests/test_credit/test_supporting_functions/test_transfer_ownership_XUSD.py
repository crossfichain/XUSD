import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time


def test_transfer_ownership(credit, xusd):
    owner = accounts[0]
    credit.transferOwnershipXUSD(accounts[1], {"from" : owner})
    
    assert xusd.owner() == accounts[1]
    
    
def test_transfer_ownership_ownable(credit, xusd):
    not_owner = accounts[1]
    with brownie.reverts("Ownable: caller is not the owner"):
        credit.transferOwnershipXUSD(accounts[1], {"from" : not_owner})
    
    assert xusd.owner() == credit.address
    
    
import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time


def test_max_amount_to_mint(credit, xusd):
    owner = accounts[0]

    value_to_set = 100_000 * 10**18
    
    credit.setMaxAmountToMint(value_to_set, {"from" : owner})
    
    assert xusd.getMaxAmountToMint() == value_to_set
    
    
def test_max_amount_to_mint_ownability(credit, xusd):
    not_owner = accounts[1]
    old_value = 500_000 * 10**18
    value_to_set = 100_000 * 10**18
    
    with brownie.reverts("Ownable: caller is not the owner"):
        credit.setMaxAmountToMint(value_to_set, {"from" : not_owner})
        xusd.setMaxAmountToMint(value_to_set, {"from" : not_owner})
        
    assert xusd.getMaxAmountToMint() == old_value
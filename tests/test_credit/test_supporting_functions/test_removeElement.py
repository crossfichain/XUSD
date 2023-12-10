import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time
import random


def test_remove_element(credit, xusd):
    collateral = Wei("1 ether")
    
    amount_XUSD = 100*10**18
    
    
    
    for i in range(5):
        account = accounts[i]
        
        credit.takeLoan(amount_XUSD, {"from" : account, "value" : collateral})
        
    credit.setTestPrice(1)
    
    for i in range(5):
        account = accounts[i]
        credit.prepareToLiquidate(account.address)
        
    positions_before = list(credit.getPositionsReadyForLiquidation())
    
    rand_num = random.randint(0,5)
    
    credit.removeElement(rand_num)
    
    positions_after = list(credit.getPositionsReadyForLiquidation())
    
    positions_before[rand_num] = positions_before[len(positions_before) - 1]
    positions_before.pop(len(positions_before) - 1)
    
    assert positions_before == positions_after
    
    for i in range(len(positions_after)):
        positions_after[i] == positions_before[i]

    
    
    
    
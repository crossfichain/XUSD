import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time

def test_existence_of_position(credit, xusd):
    with brownie.reverts("Credit: Position doesn't exist"):
        credit.prepareToLiquidate(accounts[1], {"from" : accounts[0]})
        
        
def test_ownable(credit, xusd):
    with brownie.reverts("Ownable: caller is not the owner"):
        credit.prepareToLiquidate(accounts[0], {"from" : accounts[1]})
        
        
def test_position_health(credit, xusd):
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    with brownie.reverts("Credit: Position is healthy"):
        credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
    
def test_push_to_array(credit, xusd):
    
    
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    
    credit.setTestPrice(500*10**8)
    
    credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
    
    assert credit.getPositionsReadyForLiquidation()[0][0] == user
    
    
def test_position_already_liquidating(credit, xusd):
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    
    credit.setTestPrice(500*10**8)
    
    credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
    
    assert credit.getPositionsReadyForLiquidation()[0][0] == user
    
    with brownie.reverts("Credit: Position is already liquidating"):
        credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
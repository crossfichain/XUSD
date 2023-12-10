import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time

def test_position_in_array(credit, xusd):
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    with brownie.reverts("Credit: Incorrect index"):
        credit.liquidate(user.address, 0)
        
def test_liquidation_logic(credit, xusd):
    
    liquidation_ratio = credit.liquidationRatio()
    
    liquidation_bonus = 0.1 #equals 10%
    
    penalty = 0.05 #equals 5%
    
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    liquidator = accounts[2]
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    credit.setTestPrice(599*10**8)
    
    credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
    
    credit.mintToUser(liquidator, 1000*10**18)
    
    balance_liquidator_before = liquidator.balance()
    balance_user_before = user.balance()
    
    # print(credit.getPositionsReadyForLiquidating())
    assert len(credit.getPositionsReadyForLiquidation()) == 1
    assert xusd.balanceOf(liquidator) == 1000*10**18
    
    credit.liquidate(user.address, 0, {"from" : liquidator})
    
    print("after ========", credit.getPositionsReadyForLiquidation())

    assert xusd.balanceOf(liquidator) == 1000*10**18 - amount_XUSD
    
    assert liquidator.balance() == balance_liquidator_before + collateral/liquidation_ratio + collateral*liquidation_bonus
    
    assert user.balance() == balance_user_before + (1-penalty)*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
    
    assert credit.getAccumulatedPenalties()  == penalty*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
    
    assert credit.getPositionsReadyForLiquidation() == tuple()
    
def test_many_liquidations(credit, xusd):
    liquidator = accounts[2]
    credit.mintToUser(liquidator, 100_000*10**18)
    
    amount_iterations = 10
    
    for i in range(amount_iterations):
        credit.setTestPrice(0)
        liquidation_ratio = credit.liquidationRatio()
    
        liquidation_bonus = 0.1 #equals 10%
        
        penalty = 0.05 #equals 5%
        
        collateral = Wei("0.7 ether")
        user = accounts[1]

        amount_XUSD = 200 * 10**18
        
        
        credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
        
        assert xusd.balanceOf(user) == (i+1)*amount_XUSD
        
        credit.setTestPrice(399*10**8)
        
        credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
        
        
        balance_liquidator_before = liquidator.balance()
        balance_user_before = user.balance()
        
        credit.liquidate(user.address, 0, {"from" : liquidator})
        
        assert xusd.balanceOf(liquidator) == 100_000*10**18 - (i+1)*amount_XUSD
        
        assert liquidator.balance() == balance_liquidator_before + collateral/liquidation_ratio + collateral*liquidation_bonus
        
        assert user.balance() == balance_user_before + (1-penalty)*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
        
        assert credit.getPositionsReadyForLiquidation() == tuple() 
                
    assert credit.getAccumulatedPenalties()  == amount_iterations*penalty*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
    
    
    
def test_enough_XUSD_to_liquidate(credit, xusd):
    liquidation_ratio = credit.liquidationRatio()
    
    liquidation_bonus = 0.1 #equals 10%
    
    penalty = 0.05 #equals 5%
    
    collateral = Wei("1 ether")
    user = accounts[1]
    amount_XUSD = 300 * 10**18
    
    liquidator = accounts[2]
    
    credit.takeLoan(amount_XUSD, {"from" : user, "value" : collateral})
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    credit.setTestPrice(599*10**8)
    
    credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
        
    balance_liquidator_before = liquidator.balance()
    balance_user_before = user.balance()
    
    with brownie.reverts("ERC20: burn amount exceeds balance"):
        credit.liquidate(user.address, 0, {"from" : liquidator})
    

def test_liquidation_two_positions(credit, xusd):
    
    liquidation_ratio = credit.liquidationRatio()
    
    liquidation_bonus = 0.1 #equals 10%
    
    penalty = 0.05 #equals 5%
    
    collateral = Wei("1 ether")
    user_1 = accounts[1]
    user_2 = accounts[2]
    amount_XUSD = 300 * 10**18
    
    liquidator = accounts[3]
    
    credit.takeLoan(amount_XUSD, {"from" : user_1, "value" : collateral})
    credit.takeLoan(amount_XUSD, {"from" : user_2, "value" : collateral})
    
    assert xusd.balanceOf(user_1) == amount_XUSD
    assert xusd.balanceOf(user_2) == amount_XUSD
    
    credit.setTestPrice(599*10**8)
    
    credit.prepareToLiquidate(user_1.address, {"from" : accounts[0]})
    credit.prepareToLiquidate(user_2.address, {"from" : accounts[0]})
    
    credit.mintToUser(liquidator, 1000*10**18)
    
    balance_liquidator_before = liquidator.balance()
    balance_user_1_before = user_1.balance()
    
    
    # print(credit.getPositionsReadyForLiquidating())
    assert len(credit.getPositionsReadyForLiquidation()) == 2
    assert xusd.balanceOf(liquidator) == 1000*10**18
    
    credit.liquidate(user_1.address, 0, {"from" : liquidator})
    
    print("after ========", credit.getPositionsReadyForLiquidation())

    assert xusd.balanceOf(liquidator) == 1000*10**18 - amount_XUSD
    
    assert liquidator.balance() == balance_liquidator_before + collateral/liquidation_ratio + collateral*liquidation_bonus
    
    assert user_1.balance() == balance_user_1_before + (1-penalty)*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
    
    assert credit.getAccumulatedPenalties()  == penalty*(collateral - collateral/liquidation_ratio - collateral*liquidation_bonus)
    
    position_of_user_2 = credit.getPosition(user_2)
    
    assert credit.getPositionsReadyForLiquidation()[0] == position_of_user_2
    
    assert len(credit.getPositionsReadyForLiquidation()) == 1
        

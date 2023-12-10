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

def test_take_additional_loan_1(credit, xusd):
    user = accounts[1]

    borrow_fee = credit.borrowFeePercentagePoint()/credit.precisionMultiplier()
    # print("BORROW FEE ======== ", borrow_fee)
    
    initial_amount_xusd = 100*10**18

    collateral = Wei("1 ether")

    amount_to_add = 300*10**18

    credit.takeLoan(initial_amount_xusd, {"from": user, "value": collateral})

    assert xusd.balanceOf(user) == initial_amount_xusd

    lastUpdateTime = time.time()
    credit.takeAdditionalLoan(amount_to_add, {"from" : user})
    
    assert xusd.balanceOf(user) == amount_to_add + initial_amount_xusd
    
    position = credit.getPosition(user)
    
    
    new_liquidation_price = credit.calculateLiquidationPrice(amount_to_add+initial_amount_xusd, collateral).return_value
    
    assert position[0] == user.address
    assert position[2] <= (lastUpdateTime + 1) or position[2] >= (lastUpdateTime - 1) 
    assert position[3] == collateral
    assert position[4] == amount_to_add + initial_amount_xusd
    assert position[6] == borrow_fee*(amount_to_add + initial_amount_xusd)
    assert position[7] == new_liquidation_price
    assert position[8] == True
    
def test_take_additional_loan_2(credit, xusd):
    user = accounts[1]

    borrow_fee = credit.borrowFeePercentagePoint()/credit.precisionMultiplier()
    # print("BORROW FEE ======== ", borrow_fee)
    
    initial_amount_xusd = 400*10**18

    collateral = Wei("1 ether")

    amount_to_add = 50*10**18

    credit.takeLoan(initial_amount_xusd, {"from": user, "value": collateral})

    assert xusd.balanceOf(user) == initial_amount_xusd

    lastUpdateTime = time.time()
    credit.takeAdditionalLoan(amount_to_add, {"from" : user})
    
    assert xusd.balanceOf(user) == amount_to_add + initial_amount_xusd
    
    position = credit.getPosition(user)
    
    
    new_liquidation_price = credit.calculateLiquidationPrice(amount_to_add+initial_amount_xusd, collateral).return_value
    
    assert position[0] == user.address
    assert position[2] <= (lastUpdateTime + 1) or position[2] >= (lastUpdateTime - 1) 
    assert position[3] == collateral
    assert position[4] == amount_to_add + initial_amount_xusd
    assert position[6] == borrow_fee*(amount_to_add + initial_amount_xusd)
    assert position[7] == new_liquidation_price
    assert position[8] == True
    
def test_is_available_to_mint(credit, xusd):
    user = accounts[1]

    borrow_fee = credit.borrowFeePercentagePoint()/credit.precisionMultiplier()
    # print("BORROW FEE ======== ", borrow_fee)
    
    initial_amount_xusd = 100*10**18

    collateral = Wei("4000 ether")

    amount_to_add = 500_000*10**18

    credit.takeLoan(initial_amount_xusd, {"from": user, "value": collateral})

    assert xusd.balanceOf(user) == initial_amount_xusd

    position_before = credit.getPosition(user)
    
    with brownie.reverts("XUSD: Minting Limit is exceeded"): 
        credit.takeAdditionalLoan(amount_to_add, {"from" : user})
    
    position_after = credit.getPosition(user)
    
    assert position_after == position_before
    
    

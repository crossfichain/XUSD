from monitor.event_monitor import EventMonitor
from web3 import Web3
import web3
import brownie
import json
from brownie import accounts
from brownie import Wei
import redis
from brownie import chain
import random
import time
import threading


random.seed(1231)

day = 24*3600
year = 365*day

borrow_fee = 0.01
liquidation_ratio = 2
collateral_ratio = 3

class Position():
    def __init__(self, owner, creationTime, lastUpdateTime, collateralAmount, body, interest, borrowFee, liquidationPrice, isInitialized, isLiquidating):
        self.owner = owner
        self.creationTime = creationTime
        self.lastUpdateTime = lastUpdateTime
        self.collateralAmount = collateralAmount
        self.body = body
        self.interest = interest
        self.borrowFee = borrowFee
        self.liquidationPrice = liquidationPrice
        self.isInitialized = isInitialized
        self.isLiquidating = isLiquidating
        


def take_credit(user, creditContract, xusd):
    collateral_amount = round(random.uniform(100, 500), 3)
    collateral_amount = Wei(str(collateral_amount) + " ether")
    
    balance_before = user.balance()
    amount_XUSD = random.randint(1*10**18, 400*10**18)
    
    creation_time = time.time()
    creditContract.takeLoan(amount_XUSD, {"from" : user, "value" : collateral_amount})
    
    balance_after = user.balance()
    
    liquidation_price = creditContract.calculateLiquidationPrice(amount_XUSD, collateral_amount).return_value
    
    position = Position(user, creation_time, creation_time, int(collateral_amount), int(amount_XUSD), 0, int(borrow_fee*amount_XUSD), liquidation_price, True, False)
    
    assert xusd.balanceOf(user) == amount_XUSD
    
    assert balance_before == balance_after + collateral_amount
    
    return position


def close_credit_full(user, creditContract, xusd):
    position = creditContract.getPosition(user)
    # print("position =====", position)
    collateral_amount = position[3]
    
    mint_to_user(user, creditContract)
    
    balance_before = user.balance()
    
    balance_xusd_before = xusd.balanceOf(user)
    
    creditContract.repayLoan(xusd.balanceOf(user), {"from" : user})
    
    balance_xusd_after = xusd.balanceOf(user)
    
    balance_after = user.balance()
    # print("USER = ", user.address)
    # print("collateral_amount ====", collateral_amount)
    
    # print("BALANCE BEFORE = ", balance_before)
    
    # print("BALANCE AFTEr ===", balance_after)
    
    # print("POSITION AFTER ====", creditContract.getPosition(user))
    assert balance_after == balance_before + collateral_amount
    
    assert balance_xusd_before > balance_xusd_after
    
    position = creditContract.getPosition(user)
    
    assert position == ('0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0, 0, 0, False, False)

def close_credit_partial(user, creditContract, xusd, amount_to_repay):
    position = creditContract.getPosition(user)

    balance_xusd_before = xusd.balanceOf(user)
    
    body = position[4]
        
    last_update_time = chain.time()
    
    creditContract.repayLoan(amount_to_repay, {"from" : user})
    balance_xusd_after = xusd.balanceOf(user)
    position_after = creditContract.getPosition(user)
        
    assert abs(position_after[2] - last_update_time) <=2 
    # print(position[2],position_after[2])
    assert position_after[5] > 0
    assert position_after[4] < body
    
    assert balance_xusd_before > balance_xusd_after
    


def withdraw_collateral(user, credit, xusd):
    balance_before = user.balance()
    
    position = credit.getPosition(user)
    
    collateral_amount = position[3]
    body = position[4]
    
    current_price = credit.getPriceFeeds()/10**8
    
    critical_withdraw_amount = int(collateral_amount - collateral_ratio*body/current_price)
    
    withdraw_amount = random.randint(1, critical_withdraw_amount)
    
    print("position ====", position)
    print("withdraw_amount ===", withdraw_amount)
    
    last_update_time = chain.time()
    credit.withdrawCollateralFromPosition(withdraw_amount, {"from" : user})
    
    position_after = credit.getPosition(user)
    
    assert position[3] > position_after[3]  #collateralAmount
    
    assert position[7] < position_after[7]  #liquidationPrice
    
    assert position_after[5] > position[5]  #interest
    
    assert abs(position_after[2] - last_update_time) <= 2  #lastUpdateTime
    
    assert position_after[2] > position[2] #lastUpdateTime
    
    assert position_after[6] == position[6]
    
    assert balance_before < user.balance()


def add_collateral(user, credit, xusd):
    balance_before = user.balance()
    
    position = credit.getPosition(user)
    
    collateral_amount = position[3]
    body = position[4]
    
    amount_to_add = random.randint(100, 3*10**18)
    
    last_update_time = chain.time()
    credit.addCollateral({"from" : user, "value" : amount_to_add})
    
    position_after = credit.getPosition(user)

    assert abs(position_after[2] - last_update_time) <= 2  #lastUpdateTime
    
    assert position_after[2] > position[2] #lastUpdateTime
    
    assert position_after[3] > collateral_amount  #collateralAmount
    
    assert position_after[7] < position[7]  #liquidation price
    
    assert position_after[5] > position[5] #interest
    
    assert position_after[6] == position[6]  #borrow fee

    assert user.balance() < balance_before

def take_additional_loan(user, credit, xusd):
    position = credit.getPosition(user)
    
    balance_xusd_before = xusd.balanceOf(user)
    
    current_price = credit.getPriceFeeds()/10**8
    
    collateral_amount = position[3]
    body = position[4]
    
    critical_amount_to_take = int((current_price*collateral_amount - collateral_ratio*body)/collateral_ratio)
    
    amount_to_take = random.randint(100, critical_amount_to_take)
    
    last_update_time = chain.time()
    credit.takeAdditionalLoan(amount_to_take, {"from" : user})
    
    position_after = credit.getPosition(user)

    assert abs(position_after[2] - last_update_time) <= 2  #lastUpdateTime
    
    assert position_after[2] > position[2] #lastUpdateTime
    
    assert position_after[3] == collateral_amount  #collateralAmount
    
    assert position_after[7] > position[7]  #liquidation price
    
    assert position_after[5] > position[5] #interest
    
    assert position_after[6] > position[6]  #borrow fee
    
    assert position_after[4] == int(body + amount_to_take)  #body

    assert balance_xusd_before + amount_to_take == xusd.balanceOf(user)


def liquidate(user, credit, xusd):
    
    current_price = credit.getPriceFeeds()
    
    position = credit.getPosition(user)
    
    if position[7] < current_price:
        return
    
    credit.prepareToLiquidate(user.address, {"from" : accounts[0]})
    
    position = credit.getPosition(user)
    
    assert credit.getPosition(user)[9] #isLiquidating
    
    ready_for_liquidation_positions = list(credit.getPositionsReadyForLiquidation())
    
    assert position in ready_for_liquidation_positions
    
    index = ready_for_liquidation_positions.index(position)
    
    liquidator = accounts[0]
    
    mint_to_user(liquidator, credit)
    mint_to_user(liquidator, credit)
    xusd.approve(credit.address, 10**25, {"from" : liquidator})
    
    balance_user_before = user.balance()
    
    balance_before = liquidator.balance()
    balance_xusd_before = xusd.balanceOf(liquidator)
    
    credit.liquidate(user.address, index, {"from" : liquidator})
    
    
    balance_after  = liquidator.balance()
    balance_after_xusd = xusd.balanceOf(liquidator)
    
    assert balance_after > balance_before + position[3]//liquidation_ratio
    assert balance_xusd_before - position[4] == balance_after_xusd
    
    assert user.balance() > balance_user_before
    
    new_array = list(credit.getPositionsReadyForLiquidation())
    
    assert not(position in new_array)
    
    assert credit.getPosition(user.address) == ('0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0, 0, 0, False, False)
    
    assert len(new_array) + 1 == len(ready_for_liquidation_positions)
    
    print(user, "WAS LIQUIDATED")
    

def mint_to_user(user, creditContract):
    creditContract.mintToUser(user, 1_000_000*10**18)


#description of the test:
# 100 users take credit, than all of them repay it at the different time without any issues
def test_scenario_1(credit, xusd):
    credit.setMaxAmountToMint(10**9 * 10**18)
    positions = []
    
    for i in accounts:
        if i.address == credit.address or i.address == accounts[0]:
            continue
        position = take_credit(i, credit, xusd)
        positions.append(position)
        
    for position in positions:
        position_from_contract = credit.getPosition(position.owner)

        assert position_from_contract[0] == position.owner.address
        
        assert (position_from_contract[1] >= position.creationTime - 1) or (position_from_contract[1] <= position.creationTime + 1)
        assert (position_from_contract[2] >= position.lastUpdateTime - 1) or (position_from_contract[2] <= position.lastUpdateTime + 1)
        
        assert position_from_contract[3] == position.collateralAmount
        assert position_from_contract[4] == position.body
        assert position_from_contract[5] == position.interest
        assert round(position_from_contract[6]/10**18, 6) == round(position.borrowFee/10**18, 6)
        assert position_from_contract[7] == position.liquidationPrice
        assert position_from_contract[8] == position.isInitialized
        assert position_from_contract[9] == position.isLiquidating
    
    # print("SLEEP", random.randint(30*day, year))
    chain.sleep(random.randint(30*day, year))
    
    rest_positions = []
    
    for position in positions:
        marker = bool(random.randint(0, 1))
        xusd.approve(credit.address, 10**25, {"from" : position.owner.address})
        
        
        if marker:
            close_credit_full(position.owner, credit, xusd)
        else:
            close_credit_partial(position.owner, credit, xusd, random.randint(1, position.body))
            rest_positions.append(position)
        
        chain.sleep(random.randint(10*day, 20*day))
    
    for position in rest_positions:
        close_credit_full(position.owner, credit, xusd)
        
#take a lot of credit, than call withdrawCollateral, addCollateral, takeAdditionalLoan function and close credit       
def test_scenario_2(credit, xusd):
    credit.setMaxAmountToMint(10**9 * 10**18)
    positions = []
    
    for i in accounts:
        if i.address == credit.address or i.address == accounts[0]:
            continue
        position = take_credit(i, credit, xusd)
        positions.append(position)
        
    for position in positions:
        position_from_contract = credit.getPosition(position.owner)

        assert position_from_contract[0] == position.owner.address
        
        assert (position_from_contract[1] >= position.creationTime - 1) or (position_from_contract[1] <= position.creationTime + 1)
        assert (position_from_contract[2] >= position.lastUpdateTime - 1) or (position_from_contract[2] <= position.lastUpdateTime + 1)
        
        assert position_from_contract[3] == position.collateralAmount
        assert position_from_contract[4] == position.body
        assert position_from_contract[5] == position.interest
        assert round(position_from_contract[6]/10**18, 6) == round(position.borrowFee/10**18, 6)
        assert position_from_contract[7] == position.liquidationPrice
        assert position_from_contract[8] == position.isInitialized
        assert position_from_contract[9] == position.isLiquidating
    
    # print("SLEEP", random.randint(30*day, year))
    chain.sleep(random.randint(30*day, year))
    
    
    for position in positions:
        chain.sleep(random.randint(5*day, 10*day))
        amount_actions_for_current_user = random.randint(1,4)
        for i in range(amount_actions_for_current_user):
            chain.sleep(random.randint(0.5*day, 2*day))
            marker = random.randint(1,3)
            
            if marker == 1:
                print("Inside 1!!!!!!!!")
                add_collateral(position.owner, credit, xusd)
                
            elif marker == 2:
                print("Inside 2!!!!!!!!")
                withdraw_collateral(position.owner, credit, xusd)
                
            else:
                print("Inside 3!!!!!!!!")
                take_additional_loan(position.owner, credit, xusd)
    
    
    rest_positions = []
    
    for position in positions:
        
        marker = bool(random.randint(0, 1))
        xusd.approve(credit.address, 10**25, {"from" : position.owner.address})
        
        
        if marker:
            close_credit_full(position.owner, credit, xusd)
        else:
            close_credit_partial(position.owner, credit, xusd, random.randint(1, position.body))
            rest_positions.append(position)
        
        chain.sleep(random.randint(10*day, 20*day))
    
    for position in rest_positions:
        close_credit_full(position.owner, credit, xusd)
        
        

#scenario with liquidating    
def test_scenario_with_liquidating(credit, xusd):
    credit.setMaxAmountToMint(10**9 * 10**18)
    positions = []
    
    for i in accounts:
        if i.address == credit.address or i.address == accounts[0]:
            continue
        position = take_credit(i, credit, xusd)
        positions.append(position)
        
    for position in positions:
        position_from_contract = credit.getPosition(position.owner)

        assert position_from_contract[0] == position.owner.address
        
        assert (position_from_contract[1] >= position.creationTime - 1) or (position_from_contract[1] <= position.creationTime + 1)
        assert (position_from_contract[2] >= position.lastUpdateTime - 1) or (position_from_contract[2] <= position.lastUpdateTime + 1)
        
        assert position_from_contract[3] == position.collateralAmount
        assert position_from_contract[4] == position.body
        assert position_from_contract[5] == position.interest
        assert round(position_from_contract[6]/10**18, 6) == round(position.borrowFee/10**18, 6)
        assert position_from_contract[7] == position.liquidationPrice
        assert position_from_contract[8] == position.isInitialized
        assert position_from_contract[9] == position.isLiquidating
    
    # print("SLEEP", random.randint(30*day, year))
    chain.sleep(random.randint(30*day, year))
    
    
    test_price = 1
    credit.setTestPrice(test_price)
    
    for position in positions:
        liquidate(position.owner, credit, xusd)
    
    
    
    
        

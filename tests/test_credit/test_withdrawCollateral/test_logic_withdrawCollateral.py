import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time
from brownie import chain


def test_logic(credit, xusd):
    
    user = accounts[0]

    amount_collateral = Wei("1 ether")
    amount_XUSD = 100*10**18  # 100$

    amount_withdraw = Wei("0.5 ether")

    time_before_credit = time.time()
    
    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})

    balance_before = user.balance()

    assert xusd.balanceOf(user) == amount_XUSD

    year = 31_536_000
    chain.sleep(year)
    
    credit.withdrawCollateralFromPosition(amount_withdraw, {"from": user})
    
    
    assert user.balance() == balance_before + amount_withdraw
    
    position = credit.getPosition(user)
    
    liquidation_price = credit.calculateLiquidationPrice(amount_XUSD, amount_collateral - amount_withdraw).return_value
    
    interest = credit.calculateInterest(amount_XUSD, time_before_credit).return_value
    
    assert position[0] == user.address
    assert position[3] == int(amount_collateral - amount_withdraw)
    assert position[4] == int(amount_XUSD)
    assert round(position[5]/10**18, 4) == round(interest/10**18, 4)
    assert position[6] == int(amount_XUSD*0.01)
    assert position[7] == int(liquidation_price)
    assert position[8] == True
    
    
    
def test_logic_2(credit, xusd):
    
    user = accounts[0]

    amount_collateral = Wei("2 ether")
    amount_XUSD = 300*10**18  # 100$

    amount_withdraw = Wei("1 ether")

    time_before_credit = time.time()
    
    credit.takeLoan(amount_XUSD, {"from": user, "value": amount_collateral})

    balance_before = user.balance()

    assert xusd.balanceOf(user) == amount_XUSD

    year = 31_536_000
    chain.sleep(year)
    
    credit.withdrawCollateralFromPosition(amount_withdraw, {"from": user})
    
    
    assert user.balance() == balance_before + amount_withdraw
    
    position = credit.getPosition(user)
    
    liquidation_price = credit.calculateLiquidationPrice(amount_XUSD, amount_collateral - amount_withdraw).return_value
    
    interest = credit.calculateInterest(amount_XUSD, time_before_credit).return_value
    
    assert position[0] == user.address
    assert position[3] == int(amount_collateral - amount_withdraw)
    assert position[4] == int(amount_XUSD)
    assert round(position[5]/10**18, 4) == round(interest/10**18, 4)
    assert position[6] == int(amount_XUSD*0.01)
    assert position[7] == int(liquidation_price)
    assert position[8] == True
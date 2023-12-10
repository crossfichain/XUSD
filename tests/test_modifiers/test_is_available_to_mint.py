import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import accounts
import time
import json
from web3 import Web3
from brownie import chain
from brownie import Wei


def test_is_available_to_mint_limit_by_one_mint(credit, xusd):
    AMOUNT_IN = Wei("2000 ether")
    
    
    sender = accounts[0]
    
    
    amount_to_mint = 200_000*10**18

    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})
    
    assert xusd.balanceOf(sender) == amount_to_mint


def test_is_available_to_mint_limit_by_one_mint_critical_values(credit, xusd):
    AMOUNT_IN = Wei("2000 ether")
    
        
    sender = accounts[0]
    amount_to_mint = 499_999*10**18

    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})
    
    credit.takeLoan(1*10**18, {"from" : accounts[1], "value" : AMOUNT_IN})

    with brownie.reverts("XUSD: Minting Limit is exceeded"):
        credit.takeLoan(1*10**18, {"from" : accounts[2], "value" : AMOUNT_IN})


def test_is_available_to_mint_limit_by_one_mint_reverts(credit, xusd):
    AMOUNT_IN = Wei("2000 ether")
    
        
    sender = accounts[0]
    amount_to_mint = 600_000*10**18

    with brownie.reverts("XUSD: Minting Limit is exceeded"):
        credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})
    assert xusd.balanceOf(sender) == 0

def test_is_available_to_mint_limit_per_day(credit, xusd):
    AMOUNT_IN = Wei("2000 ether")
    
        
    sender = accounts[0]
    amount_to_mint = 200_000*10**18

    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})
    credit.takeLoan(amount_to_mint, {"from" : accounts[1], "value" : AMOUNT_IN})

    with brownie.reverts("XUSD: Minting Limit is exceeded"):
        credit.takeLoan(amount_to_mint, {"from" : accounts[2], "value" : AMOUNT_IN})


def test_is_available_to_mint_updating_time(credit, xusd):
    AMOUNT_IN = Wei("2000 ether")
    
    
    sender = accounts[0]
    amount_to_mint = 400_000 * 10**18
    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})
    
    assert xusd.balanceOf(sender) == amount_to_mint

    day = 86400 + 1
    chain.sleep(day)

    credit.takeLoan(amount_to_mint, {"from" : accounts[1], "value" : AMOUNT_IN})
    
    assert xusd.balanceOf(accounts[1]) == amount_to_mint


def test_is_available_to_mint_updating_time_revert(credit, xusd):
    AMOUNT_IN = Wei("1000 ether")
    
        
    sender = accounts[0]
    amount_to_mint = 400_000 * 10**18
    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})

    half_day = (86400 + 1)//2
    chain.sleep(half_day)

    with brownie.reverts("XUSD: Minting Limit is exceeded"):
        credit.takeLoan(amount_to_mint, {"from" : accounts[1], "value" : AMOUNT_IN})


def test_is_available_to_mint_updating_critical_values(credit, xusd):
    AMOUNT_IN = Wei("1000 ether")
    
   
    sender = accounts[0]
    amount_to_mint = 400_000 * 10**18
    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : AMOUNT_IN})

    almost_day = 86400 - 10
    chain.sleep(almost_day)

    with brownie.reverts("XUSD: Minting Limit is exceeded"):
        credit.takeLoan(amount_to_mint, {"from" : accounts[1], "value" : AMOUNT_IN})

    chain.sleep(11)
    credit.takeLoan(amount_to_mint, {"from" : accounts[1], "value" : AMOUNT_IN})

    assert xusd.balanceOf(accounts[1]) == amount_to_mint
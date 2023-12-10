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

def test_value_greater_than_zero(credit, xusd):
    sender = accounts[0]
    
    
    
    with brownie.reverts("Credit: Sent incorrect collateral amount"):
        credit.addCollateral({"from" : sender, "value" : 0})
        
        
def test_existence(credit, xusd):
    sender = accounts[0]
    
    amount = "1 ether"
    
    with brownie.reverts("Credit: Position doesn't exist"):
        credit.addCollateral({"from" : sender, "value" : amount})
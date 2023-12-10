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


def test_modifier(credit, xusd):
    owner = accounts[0]
    
    user = accounts[1]
    
    
    credit.pause({"from" : owner})
    
    with brownie.reverts("Pausable: paused"):
        credit.addCollateral({"from" : user, "value" : 1})
    
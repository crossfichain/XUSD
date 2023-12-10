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


def test_creating_position(credit, xusd):
    
    
    sender = accounts[1]

    amount_to_mint = 100*10**18

    amount_XFI_to_send = Wei("1 ether")

    credit.takeLoan(amount_to_mint, {
        "from": sender, "value": amount_XFI_to_send})
    
    liquidation_price = credit.calculateLiquidationPrice(amount_to_mint, amount_XFI_to_send).return_value
    # print("liquidation_price = ", liquidation_price)
    now = time.time()
    
    created_position = credit.getPosition(sender.address)
    
    assert created_position[0] == sender.address
    assert (created_position[1] >= int(now) - 1) or (created_position[1] <= int(now) + 1)
    assert (created_position[2] >= int(now) - 1) or (created_position[2] <= int(now) + 1)
    assert created_position[3] == int(amount_XFI_to_send)
    assert created_position[4] == int(amount_to_mint)
    assert created_position[5] == 0
    assert created_position[6] == int(amount_to_mint*0.01)
    assert created_position[7] == liquidation_price
    assert created_position[8] == True
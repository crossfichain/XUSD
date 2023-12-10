import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
import time


def test_create_new_position(credit, xusd,  accounts):
    sender = accounts[0]
    collateral_amount = 2000*10**18
    amount_out = 500*10**18

    liquidation_price = 500*10**8

    now = time.time()
    credit.createNewPosition(
        sender, collateral_amount, amount_out, liquidation_price)
    
    created_position = credit.getPosition(sender.address)

    assert created_position[0] == sender.address
    assert (created_position[1] >= int(now) - 1) or (created_position[1] <= int(now) + 1)
    assert (created_position[2] >= int(now) - 1) or (created_position[2] <= int(now) + 1)
    assert created_position[3] == int(collateral_amount)
    assert created_position[4] == int(amount_out)
    assert created_position[5] == 0
    assert created_position[6] == int(amount_out*0.01)
    assert created_position[7] == int(liquidation_price)
    assert created_position[8] == True

def test_empty_position(credit, xusd):
    empty_pos_address = accounts[1]
    
    empty_pos_example = ('0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0, 0, 0, False, False)
    
    position = credit.getPosition(empty_pos_address)
    
    assert position == empty_pos_example
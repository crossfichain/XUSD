import brownie
from brownie import web3
from brownie import accounts
from brownie import Wei
import time
from brownie import chain

def test_update(credit, xusd):
    sender = accounts[0]
    
    amount_to_mint = 500 * 10**18
    amount_in = "1 ether"
    
    creation_time = time.time()
    credit.takeLoan(amount_to_mint, {"from" : sender, "value" : amount_in})
    
    assert xusd.balanceOf(sender) == amount_to_mint
    
    
    new_collateral_amount = Wei("4 ether")
    new_body = 200 * 10**18
    new_interest = 101
    new_borrow_fee = 202
    
    chain.sleep(4412)
    last_update_time = time.time()
    
    credit.updatePosition(sender, new_collateral_amount, new_body, new_interest, new_borrow_fee)
    
    position = credit.getPosition(sender)
    
    print(position)
    
    liquidation_price = credit.calculateLiquidationPrice(new_body, new_collateral_amount).return_value
    
    assert position[0] == sender.address
    assert (position[1] >= int(creation_time) - 1) or (position[1] <= int(creation_time) + 1)
    assert (position[2] >= int(last_update_time) - 1) or (position[2] <= int(last_update_time) + 1)
    assert position[3] == int(new_collateral_amount)
    assert position[4] == int(new_body)
    assert position[5] == new_interest
    assert position[6] == int(new_borrow_fee)
    assert position[7] == int(liquidation_price)
    assert position[8] == True
    
    
    
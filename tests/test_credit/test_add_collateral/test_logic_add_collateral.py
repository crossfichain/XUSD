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

def test_add_collateral(credit, xusd):
    user = accounts[1]
    
    amount_collateral = Wei("1 ether")
    
    amount_collateral_to_add = Wei("0.5 ether")
    
    amount_to_mint = 1 * 10 ** 18
    
    interest = 0.05
    
    creation_time = time.time()
    credit.takeLoan(amount_to_mint, {"from" : user, "value" : amount_collateral})
    
    assert credit.getPosition(user.address)[0] == user.address
    
    year = 31_536_000
    chain.sleep(year)
    
    update_time = time.time()
    
    credit.addCollateral({"from" : user, "value" : amount_collateral_to_add})
    position = credit.getPosition(user)
    
    print("POSITION ===== ", position)
    
    new_liquidation_price = credit.calculateLiquidationPrice(amount_to_mint, amount_collateral+amount_collateral_to_add).return_value
    
    assert position[0] == user.address
    assert (position[1] >= int(creation_time) - 1) or (position[1] <= int(creation_time) + 1)
    assert (position[2] >= int(update_time) - 1) or (position[2] <= int(update_time) + 1)
    assert position[3] == int(amount_collateral + amount_collateral_to_add)
    assert position[4] == int(amount_to_mint) #body
    assert round(position[5]/10**18, 5) == round(int(amount_to_mint*interest)/10**18, 5)                     #interest
    assert position[6] == int(amount_to_mint*0.01)
    assert position[7] == int(new_liquidation_price)
    assert position[8] == True
    
    
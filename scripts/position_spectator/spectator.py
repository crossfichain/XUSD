from monitor.event_monitor import EventMonitor
from web3 import Web3
import web3
import brownie
import json
from brownie import accounts
from brownie import Wei
import redis



def init(credit):
    amount_collateral = Wei("2 ether")
    for i in range(5):
        credit.functions.takeLoan((i+1)*100*10**18).transact({"from" : accounts[i+2].address, "value" : amount_collateral})

def check_positions_health(credit_address):
    with open('ABI/Credit.json', 'r') as f:
        creditAbi = json.loads(f.read())


    contract_owner = accounts[0]

    web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545", request_kwargs={"timeout" : 240}))

    database = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    CreditContract = web3.eth.contract(address=credit_address, abi=creditAbi)
    
    
    current_price = int(CreditContract.functions.getPriceFeeds().call())
    # init(CreditContract)
    for key in database.scan_iter():
        position = database.hgetall(key)
        
        liquidation_price = int(position["liquidationPrice"])
        
        
        if current_price < liquidation_price:
            CreditContract.functions.prepareToLiquidate(position["owner"]).transact({"from" : contract_owner.address})
    print("END")
        
    
def main():
    check_positions_health("0xed00238F9A0F7b4d93842033cdF56cCB32C781c2")
    
    



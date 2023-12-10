from monitor.event_monitor import EventMonitor
from web3 import Web3
import web3
import brownie
import json
from brownie import accounts
from brownie import Wei
import redis
from brownie import chain


with open('ABI/CreditTest.json', 'r') as f:
    creditAbi = json.loads(f.read())

web3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545", request_kwargs={"timeout" : 240}))

contract_owner = accounts[0]

liquidator_account = accounts[8]

def mintXUSD(user_address, credit_address):
    print(user_address)
    CreditContract = web3.eth.contract(address=credit_address, abi=creditAbi)
    day = 86400
    CreditContract.functions.mintToUser(user_address, 400_000 * 10**18).transact({"from" : contract_owner.address})
    chain.sleep(day+1)

def liquidator(credit_address):
    
    CreditContract = web3.eth.contract(address=credit_address, abi=creditAbi)
    
    while True:
        try:
            positions = CreditContract.functions.getPositionsReadyForLiquidation().call()
            
            print(len(positions))
            # exit(32)
            
            if(len(positions) == 0):
                continue
            
            for i in range(len(positions)):
                position = positions[i]
                
                owner = position[0]
                print("OWNER = ", owner)
                print("LIQ = ", liquidator_account)
                CreditContract.functions.liquidate(owner, 0).transact({"from" : liquidator_account.address})
                
                print("LIQUIDATED.................", owner)
                
        except Exception as error:
            print(error)
            # pass
            
            
def main():
    # mintXUSD(liquidator_account.address, "0xed00238F9A0F7b4d93842033cdF56cCB32C781c2")
    
    liquidator("0xed00238F9A0F7b4d93842033cdF56cCB32C781c2")

        

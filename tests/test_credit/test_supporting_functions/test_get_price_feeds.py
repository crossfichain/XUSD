import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
import time
import json
from web3 import Web3

with open('ABI/ORACLE.json') as f:
    ORACLE_ABI = json.loads(f.read())


# web3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:8545',
#             request_kwargs={'timeout': 240}))


def test_get_price_feeds(xusd, credit, accounts):
    sender = accounts[0]

    address_oracle = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"

    OracleContract = web3.eth.contract(address=address_oracle, abi=ORACLE_ABI)
    price_from_oracle = OracleContract.functions.latestAnswer().call()

    price_from_credit_contract = credit.getPriceFeeds()

    print("price_from_credit_contract ", price_from_credit_contract)
    print("Price from Oracle = ", price_from_oracle)

    assert price_from_credit_contract == price_from_oracle

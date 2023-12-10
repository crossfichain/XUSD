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


def test_calc_interest_1(credit, xusd):
    real_interest_per_year = 0.05
    body = 10000
    
    last_update_time = time.time()
    
    one_year = 31_536_000
    
    chain.sleep(one_year)
    
    interest = credit.calculateInterest(body, last_update_time).return_value
    
    assert  interest == real_interest_per_year*body
    
    
def test_calc_interest_2(credit, xusd):
    real_interest_per_year = 0.05
    body = 100 * 10**18
    
    last_update_time = time.time()
    
    half_year = int(31_536_000/2)
    
    chain.sleep(half_year)
    
    interest = credit.calculateInterest(body, last_update_time).return_value
    
    # print("interest = ", interest)
    assert  round(interest/10**18, 4) == round(int(real_interest_per_year*body/2)/10**18, 4)
    
    
    
def test_calc_interest_3(credit, xusd):
    real_interest_per_year = 0.05
    body = 360 * 10**18
    
    
    
    four_month = int(4 * 2_628_000)
    last_update_time = time.time()
    chain.sleep(four_month)
    
    interest = credit.calculateInterest(body, last_update_time).return_value
    
    # print("interest = ", interest)
    assert round(interest/10**18, 4) == round(int(real_interest_per_year*body/3)/10**18, 4)
    
def test_calc_interest_4(credit, xusd):
    real_interest_per_year = 0.05
    body = 12331 * 10**18
    
    
    
    one_month = int(2_628_000)
    last_update_time = time.time()
    chain.sleep(one_month)
    
    interest = credit.calculateInterest(body, last_update_time).return_value
    
    # print("interest = ", interest)
    assert round(interest/10**18, 4) == round(int(real_interest_per_year*body/12)/10**18, 4)
    
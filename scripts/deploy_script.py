from brownie import accounts
from brownie import XUSD
from brownie import CreditTest


def deploy():
    deployer = accounts[0]

    credit = CreditTest.deploy({"from": deployer})
    
    credit_deployer = accounts[0]
    deployer = credit.address

    xusd = XUSD.deploy(deployer, {"from": deployer})
    credit.init(xusd.address, "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419")
    
    return credit, xusd

def main():
    deploy()
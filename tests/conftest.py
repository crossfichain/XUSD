#!/usr/bin/python3

import pytest
from brownie import accounts


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    # perform a chain rewind after completing each test, to ensure proper isolation
    # https://eth-brownie.readthedocs.io/en/v1.10.3/tests-pytest-intro.html#isolation-fixtures
    pass


@pytest.fixture(scope="module")
def token(Token, accounts):
    return Token.deploy("Test Token", "TST", 18, 1e21, {'from': accounts[0]})


@pytest.fixture(scope="module")
def credit(CreditTest, accounts):
    deployer = accounts[0]

    credit = CreditTest.deploy({"from": deployer})
    return credit


@pytest.fixture(scope="module")
def xusd(XUSD, accounts, credit):
    credit_deployer = accounts[0]
    deployer = credit.address

    xusd = XUSD.deploy(deployer, {"from": deployer})
    credit.init(xusd.address, "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419")
    return xusd

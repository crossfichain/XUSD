from monitor.event_monitor import EventMonitor
import redis
import random, time
from brownie import chain

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def test_event_syncer(credit, xusd,  accounts):
    monitor = EventMonitor(credit.address, credit.tx.block_number)
    monitor.stop()

    account = accounts[1]
    if r.exists(account.address):
        r.delete(account.address)

    # for account in accounts:
    loan_amount = random.randint(0, 500) * 10**18
    collateral = "2 ether"
    created_position = take_loan(credit, account, collateral, loan_amount)

    chain.sleep(1000000)

    repay_amount = random.randint(300, 400) * 10**18
    repay_loan(credit, xusd, account, repay_amount)


    chain.sleep(1000000)

    # monitor = EventMonitor(credit.address, credit.tx.block_number)
    monitor.sync_events()
    repayed_position = credit.getPosition(account.address)

    # for account in accounts:
    # time.sleep(5)
    db_record = r.hgetall(account.address)

    print(f'\n\n\n{repayed_position}\n{db_record}\n\n\n\n')

    assert (repayed_position[0] == db_record["owner"]) or (repayed_position[0] == '0x0000000000000000000000000000000000000000')
    assert repayed_position[1] == db_record["creationTime"]
    assert (repayed_position[2] == db_record["lastUpdateTime"]) or (repayed_position[2] == 0)
    assert repayed_position[3] == db_record["collateralAmount"]
    assert repayed_position[4] == db_record["body"]
    assert repayed_position[5] == db_record["interest"]
    assert repayed_position[6] == db_record["borrowFee"]
    assert repayed_position[7] == db_record["liquidationPrice"]

    r.delete(account.address)
    monitor.stop()


def take_loan(credit, sender, collateral, loan_body):
    credit.takeLoan(loan_body, {
        "from": sender, "value": collateral})
    created_position = credit.getPosition(sender.address)

    return created_position

def repay_loan(credit, xusd, sender, repay_amount):
    xusd.approve(credit, repay_amount, {"from": sender})
    XUSD_balance = xusd.balanceOf(sender)

    if XUSD_balance < repay_amount:
        xusd.mint(sender, repay_amount - XUSD_balance, {"from": credit})
    
    credit.repayLoan(repay_amount, {"from": sender})
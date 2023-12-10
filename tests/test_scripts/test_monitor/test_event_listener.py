# import scripts.get_positions.event_monitor
from monitor.event_monitor import EventMonitor
import time
import redis
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def test_event_listener(credit, xusd,  accounts):
    monitor = EventMonitor(credit.address, credit.tx.block_number)

    account = accounts[0]
    if r.exists(account.address):
        r.delete(account.address)
    # for account in accounts[:5]:
    loan_amount = random.randint(0, 500) * 10**18
    collateral = "2 ether"
    created_position = take_loan(credit, account, collateral, loan_amount)

    time.sleep(9)
    db_record = r.hgetall(account.address)

    assert created_position[0] == db_record["owner"]
    assert created_position[1] == db_record["creationTime"]
    assert created_position[2] == db_record["lastUpdateTime"]
    assert created_position[3] == db_record["collateralAmount"]
    assert created_position[4] == db_record["body"]
    assert created_position[5] == db_record["interest"]
    assert created_position[6] == db_record["borrowFee"]
    assert created_position[7] == db_record["liquidationPrice"]

    repay_amount = random.randint(300, 700) * 10**18
    repayed_position = repay_loan(credit, xusd, account, repay_amount)

    time.sleep(8)
    db_record_updated = r.hgetall(account.address)

    print(f'\n\n\n{repayed_position}\n{db_record_updated}\n\n\n\n')


    assert (repayed_position[0] == db_record_updated["owner"]) or (repayed_position[0] == '0x0000000000000000000000000000000000000000')
    assert repayed_position[1] == db_record_updated["creationTime"]
    assert (repayed_position[2] == db_record_updated["lastUpdateTime"]) or (repayed_position[2] == 0)
    assert repayed_position[3] == db_record_updated["collateralAmount"]
    assert repayed_position[4] == db_record_updated["body"]
    assert repayed_position[5] == db_record_updated["interest"]
    assert repayed_position[6] == db_record_updated["borrowFee"]
    assert repayed_position[7] == db_record_updated["liquidationPrice"]

    r.delete(account.address)
    monitor.stop()

    


def take_loan(credit, sender, collateral, loan_body):
    credit.takeLoan(loan_body, {
        "from": sender, "value": collateral})
    return credit.getPosition(sender.address)


def repay_loan(credit, xusd, sender, repay_amount):
    xusd.approve(credit, repay_amount, {"from": sender})
    XUSD_balance = xusd.balanceOf(sender)

    if XUSD_balance < repay_amount:
        xusd.mint(sender, repay_amount - XUSD_balance, {"from": credit})    
    credit.repayLoan(repay_amount, {"from": sender})
    return credit.getPosition(sender.address)


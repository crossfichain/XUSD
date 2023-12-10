import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time


def test_repay_loan(credit, xusd,  accounts):
    sender = accounts[0]
    amount_to_mint = 100*10**18
    amount_XFI_to_send = Wei("1 ether")
    credit.takeLoan(amount_to_mint, {
        "from": sender, "value": amount_XFI_to_send})
    now = time.time()
    created_position = credit.getPosition(sender.address)

    print_position(created_position)


    additional_XUSDs = 500 * 10**18
    xusd.mint(sender, additional_XUSDs, {"from": credit})

    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})

    sender_XUSD_balance = xusd.balanceOf(sender)
    contract_balance = credit.balance()
    sender_balance = sender.balance()

    assert sender_XUSD_balance == amount_to_mint + additional_XUSDs
    assert contract_balance >= amount_XFI_to_send
    
    credit.repayLoan(sender_XUSD_balance, {"from": sender})

    calculaed_interest = credit.calculateInterest(int(amount_to_mint), created_position[2]).return_value
    repayed_position = credit.getPosition(sender.address) 

    new_sender_XUSD_balance = xusd.balanceOf(sender)
    new_contract_balance = credit.balance()
    new_sender_balance = sender.balance()

    new_sender_XUSD_balance = round(new_sender_XUSD_balance/10**18, 6)
    new_sender_XUSD_balance_calculated = round((sender_XUSD_balance - amount_to_mint - calculaed_interest - int(amount_to_mint*0.01))/10**18, 6)
    print(f'New sender {new_sender_XUSD_balance} Calculated: {new_sender_XUSD_balance_calculated}')

    assert new_sender_XUSD_balance == new_sender_XUSD_balance_calculated
    assert new_contract_balance >= contract_balance - amount_XFI_to_send
    assert new_sender_balance == sender_balance + amount_XFI_to_send

    empty_position = ('0x0000000000000000000000000000000000000000', 0, 0, 0, 0, 0, 0, 0, False, False)

    assert repayed_position == empty_position


def print_position(position):
    output = f'Debtor: {position[0]}\
        \nCreation time: {position[1]}\
        \nLast update time: {position[2]}\
        \nColalteral amount: {position[3]}\
        \nBody amount: {position[4]}\
        \nInterest amount: {position[5]}\
        \nBorrow Fee amount: {position[6]}\
        \nLiquidation price: {position[7]}\
        \nIs Initialized: {position[8]}'

    print(output)
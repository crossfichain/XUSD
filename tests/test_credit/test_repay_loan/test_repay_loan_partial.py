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


    spend_tokens = 50 * 10**18
    xusd.burn(sender, spend_tokens, {"from": credit})

    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})

    sender_XUSD_balance = xusd.balanceOf(sender)
    contract_balance = credit.balance()
    sender_balance = sender.balance()


    assert sender_XUSD_balance == amount_to_mint - spend_tokens
    assert contract_balance >= amount_XFI_to_send    


    # print("\n\n\n")
    # print(f'XUSD balance of sender: {xusd.balanceOf(sender)}')
    # print(f'Contract balance: {credit.balance()}')
    # print(f'Sender balance: {sender.balance()}')
    # print("\n\n\n")


    credit.repayLoan(sender_XUSD_balance, {"from": sender})
    liquidation_price = credit.calculateLiquidationPrice(int(amount_to_mint - sender_XUSD_balance), amount_XFI_to_send).return_value


    calculaed_interest = credit.calculateInterest(created_position[4], created_position[2]).return_value
    repayed_position = credit.getPosition(sender.address)
    interest_from_posotion = round(repayed_position[5] / 10**18, 6)
    calculaed_interest_rounded = round(calculaed_interest / 10**18, 6) 

    assert repayed_position[0] == sender.address
    assert (repayed_position[1] >= int(now) - 1) or (repayed_position[1] <= int(now) + 1)
    assert (repayed_position[2] >= int(now) - 1) or (repayed_position[2] <= int(now) + 1)
    assert repayed_position[3] == int(amount_XFI_to_send)
    assert repayed_position[4] == int(amount_to_mint - sender_XUSD_balance)
    assert interest_from_posotion == calculaed_interest_rounded
    assert repayed_position[6] == int(amount_to_mint*0.01)
    assert repayed_position[7] == liquidation_price
    assert repayed_position[8] == True


    new_sender_XUSD_balance = xusd.balanceOf(sender)
    new_contract_balance = credit.balance()
    new_sender_balance = sender.balance()

    assert new_sender_XUSD_balance == 0 
    assert new_contract_balance >= contract_balance
    assert new_sender_balance == sender_balance



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
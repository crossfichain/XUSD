import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time


def test_repay_loan_only_body(credit, xusd,  accounts):
    sender = accounts[0]
    created_position = take_loan(credit, sender)
    amount_borrowed_XUSDs = created_position[4]
    collateral_amount = created_position[3]

    print_position(created_position)

    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})

    sender_XUSD_balance = xusd.balanceOf(sender)
    contract_balance = credit.balance()
    sender_balance = sender.balance()
    total_XUSD_amount = xusd.totalSupply()
    acumulated_fees = credit.getAccumulatedFees().return_value

    print(f"Total XUSD: {total_XUSD_amount}\nAccumulatedFees: {acumulated_fees}")

    assert sender_XUSD_balance == amount_borrowed_XUSDs
    assert contract_balance >= collateral_amount
    
    credit.repayLoan(sender_XUSD_balance, {"from": sender})

    calculaed_interest = credit.calculateInterest(int(amount_borrowed_XUSDs), created_position[2]).return_value
    repayed_position = credit.getPosition(sender.address)
    liquidation_price = credit.calculateLiquidationPrice(int(amount_borrowed_XUSDs - sender_XUSD_balance), collateral_amount).return_value

    print_position(repayed_position) 

    new_sender_XUSD_balance = xusd.balanceOf(sender)
    new_contract_balance = credit.balance()
    new_sender_balance = sender.balance()
    new_total_XUSD_amount = xusd.totalSupply()
    new_acumulated_fees = credit.getAccumulatedFees().return_value
    print(f"Total XUSD: {new_total_XUSD_amount}\nAccumulatedFees: {new_acumulated_fees}")

    assert new_sender_XUSD_balance == 0
    assert new_contract_balance == contract_balance
    assert new_sender_balance == sender_balance
    assert new_total_XUSD_amount == total_XUSD_amount - amount_borrowed_XUSDs
    assert new_acumulated_fees == acumulated_fees
    

    interest_from_position = round(repayed_position[5] / 10**18, 6)
    calculaed_interest_rounded = round(calculaed_interest / 10**18, 6) 

    assert repayed_position[0] == sender.address
    assert repayed_position[1] <= repayed_position[2]
    assert repayed_position[3] == int(collateral_amount)
    assert repayed_position[4] == 0
    assert interest_from_position == calculaed_interest_rounded
    assert repayed_position[6] == int(amount_borrowed_XUSDs*0.01)
    assert repayed_position[7] == liquidation_price
    assert repayed_position[8] == True



def test_repay_loan_only_part_of_body(credit, xusd,  accounts):
    sender = accounts[0]
    created_position = take_loan(credit, sender)
    amount_borrowed_XUSDs = created_position[4]
    collateral_amount = created_position[3]

    print_position(created_position)

    # additional_XUSDs = 500 * 10**18
    # xusd.mint(sender, additional_XUSDs, {"from": credit})
    spend_tokens = 75 * 10**18
    xusd.burn(sender, spend_tokens, {"from": credit})

    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})

    sender_XUSD_balance = xusd.balanceOf(sender)
    print(f'Sender balance XUSD {sender_XUSD_balance}')
    contract_balance = credit.balance()
    sender_balance = sender.balance()
    total_XUSD_amount = xusd.totalSupply()
    acumulated_fees = credit.getAccumulatedFees().return_value

    print(f"Total XUSD: {total_XUSD_amount}\nAccumulatedFees: {acumulated_fees}")

    assert sender_XUSD_balance == amount_borrowed_XUSDs - spend_tokens
    assert contract_balance >= collateral_amount
    
    credit.repayLoan(sender_XUSD_balance, {"from": sender})

    calculaed_interest = credit.calculateInterest(int(amount_borrowed_XUSDs), created_position[2]).return_value
    repayed_position = credit.getPosition(sender.address)
    liquidation_price = credit.calculateLiquidationPrice(int(amount_borrowed_XUSDs - sender_XUSD_balance), collateral_amount).return_value
    print_position(repayed_position)

    new_sender_XUSD_balance = xusd.balanceOf(sender)
    new_contract_balance = credit.balance()
    new_sender_balance = sender.balance()
    new_total_XUSD_amount = xusd.totalSupply()
    new_acumulated_fees = credit.getAccumulatedFees().return_value
    print(f"Total XUSD: {new_total_XUSD_amount}\nAccumulatedFees: {new_acumulated_fees}")

    assert new_sender_XUSD_balance == 0
    assert new_contract_balance == contract_balance
    assert new_sender_balance == sender_balance
    assert new_total_XUSD_amount == total_XUSD_amount - sender_XUSD_balance
    assert new_acumulated_fees == acumulated_fees

    interest_from_position = round(repayed_position[5] / 10**18, 6)
    calculaed_interest_rounded = round(calculaed_interest / 10**18, 6) 

    assert repayed_position[0] == sender.address
    # assert repayed_position[1] != repayed_position[2]
    assert repayed_position[3] == int(collateral_amount)
    assert repayed_position[4] == amount_borrowed_XUSDs - sender_XUSD_balance
    assert interest_from_position == calculaed_interest_rounded
    assert repayed_position[6] == int(amount_borrowed_XUSDs*0.01)
    assert repayed_position[7] == liquidation_price
    assert repayed_position[8] == True



def test_repay_loan_body_and_interest(credit, xusd,  accounts):
    sender = accounts[0]
    created_position = take_loan(credit, sender)
    amount_borrowed_XUSDs = created_position[4]
    collateral_amount = created_position[3]

    print_position(created_position)

    time.sleep(1)
    calculaed_interest = credit.calculateInterest(int(amount_borrowed_XUSDs), created_position[2]).return_value
    print(f'Calculated interest: {calculaed_interest}')
    calculaed_interest_rounded = round(calculaed_interest / 10**18, 7)
    additional_XUSDs = calculaed_interest_rounded * 10**18 # + 2*10**12
    xusd.mint(sender, additional_XUSDs, {"from": credit})

    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})

    sender_XUSD_balance = xusd.balanceOf(sender)
    print(f'Sender balance XUSD {sender_XUSD_balance}')
    contract_balance = credit.balance()
    sender_balance = sender.balance()
    total_XUSD_amount = xusd.totalSupply()
    acumulated_fees = credit.getAccumulatedFees().return_value

    print(f"Total XUSD: {total_XUSD_amount}\nAccumulatedFees: {acumulated_fees}")

    # assert sender_XUSD_balance == amount_borrowed_XUSDs + additional_XUSDs
    # assert contract_balance >= collateral_amount
    
    credit.repayLoan(sender_XUSD_balance, {"from": sender})

    repayed_position = credit.getPosition(sender.address)
    liquidation_price = credit.calculateLiquidationPrice(int(amount_borrowed_XUSDs - sender_XUSD_balance), collateral_amount).return_value if amount_borrowed_XUSDs > sender_XUSD_balance else credit.calculateLiquidationPrice(int(0), collateral_amount).return_value
    print_position(repayed_position)

    new_sender_XUSD_balance = xusd.balanceOf(sender)
    new_contract_balance = credit.balance()
    new_sender_balance = sender.balance()
    new_total_XUSD_amount = xusd.totalSupply()
    new_acumulated_fees = credit.getAccumulatedFees().return_value
    print(f"Total XUSD: {new_total_XUSD_amount}\nAccumulatedFees: {new_acumulated_fees}")

    assert new_sender_XUSD_balance == 0
    assert new_contract_balance == contract_balance
    assert new_sender_balance == sender_balance
    assert new_total_XUSD_amount >= total_XUSD_amount - amount_borrowed_XUSDs
    assert new_acumulated_fees == acumulated_fees + additional_XUSDs

    interest_from_position = round(repayed_position[5] / 10**18, 6)
    borrow_fee_from_position = round(repayed_position[6] / 10**18, 2) * 10**18

    assert repayed_position[0] == sender.address
    assert repayed_position[1] != repayed_position[2]
    assert repayed_position[3] == int(collateral_amount)
    assert repayed_position[4] == 0
    assert interest_from_position == 0
    assert borrow_fee_from_position == int(amount_borrowed_XUSDs*0.01 )
    assert repayed_position[7] == liquidation_price
    assert repayed_position[8] == True








def take_loan(credit, sender):    
    amount_to_mint = 100*10**18
    amount_XFI_to_send = Wei("1 ether")
    tx_loan = credit.takeLoan(amount_to_mint, {
        "from": sender, "value": amount_XFI_to_send})
    created_position = credit.getPosition(sender.address)

    return created_position



def print_position(position):
    output = f'\n\n{100*"#"}\
        \nDebtor: {position[0]}\
        \nCreation time: {position[1]}\
        \nLast update time: {position[2]}\
        \nColalteral amount: {position[3]}\
        \nBody amount: {position[4]}\
        \nInterest amount: {position[5]}\
        \nBorrow Fee amount: {position[6]}\
        \nLiquidation price: {position[7]}\
        \nIs Initialized: {position[8]}\
        \n{100*"#"}\n\n'

    print(output)
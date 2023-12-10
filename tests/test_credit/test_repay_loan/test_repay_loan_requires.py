import brownie
from brownie import web3
from brownie import accounts
from brownie import XUSD
from brownie import CreditTest
from brownie import Wei
import time



def test_repay_loan_allowance_check(credit, xusd,  accounts):
    sender = accounts[0]
    created_position = take_loan(credit, sender)
    amount_borrowed_XUSDs = created_position[4]
    collateral_amount = created_position[3]

    with brownie.reverts("ERC20: insufficient allowance"):
        credit.repayLoan(amount_borrowed_XUSDs, {"from": sender})


# def test_repay_loan_close_position_with_debt_check(credit, xusd,  accounts):
#     sender = accounts[0]
#     created_position = take_loan(credit, sender)
#     amount_borrowed_XUSDs = created_position[4]
#     collateral_amount = created_position[3]

#     with brownie.reverts("Credit: the debt is not zero"):
#         credit.closePosition(sender, amount_borrowed_XUSDs, {"from": sender})
    
#     allowance_to_repay = 1000 * 10**18
#     xusd.approve(credit, allowance_to_repay, {"from": sender})

#     credit.repayLoan(amount_borrowed_XUSDs, {"from": sender})

#     with brownie.reverts("Credit: the debt is not zero"):
#         credit.closePosition(sender, amount_borrowed_XUSDs, {"from": sender})


def _test_repay_loan_close_position_with_insuffisent_contract_balance(credit, xusd,  accounts):
    sender = accounts[0]
    created_position = take_loan(credit, sender)
    amount_borrowed_XUSDs = created_position[4]
    collateral_amount = created_position[3]

    print(credit.balance())
    print(sender.balance())

    print_position(created_position)

    credit.withdrawXFI({"from": sender})

    additional_XUSDs = 500 * 10**18
    xusd.mint(sender, additional_XUSDs, {"from": credit})


    allowance_to_repay = 1000 * 10**18
    xusd.approve(credit, allowance_to_repay, {"from": sender})
    print(credit.balance())
    print(sender.balance())

    

    with brownie.reverts("Credit: Contract can't return collateral"):
        credit.repayLoan(sender.balance(), {"from": sender})

    repayed_position = credit.getPosition(sender.address)

    print_position(repayed_position)    


def take_loan(credit, sender):    
    amount_to_mint = 100*10**18
    amount_XFI_to_send = Wei("1 ether")
    credit.takeLoan(amount_to_mint, {
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
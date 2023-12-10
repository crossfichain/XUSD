// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/security/Pausable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/token/ERC20/IERC20.sol";
import "interfaces/IChainlinkPriceOracle.sol";
import "contracts/Credit.sol";
import "contracts/XUSD.sol";

contract CreditTest is Credit {
    int public testPrice = 0;

    function createNewPosition(
        address _sender,
        uint _collateralAmount,
        uint _body,
        uint _liquidationPrice
    ) external {
        _createNewPosition(
            _sender,
            _collateralAmount,
            _body,
            _liquidationPrice
        );
    }

    function calculateLiquidationPrice(
        uint amountXUSD,
        uint collateralAmount
    ) external returns (uint) {
        return _calculateLiquidationPrice(amountXUSD, collateralAmount);
    }
    function updatePosition(address owner, uint newCollateralAmount, uint newBody, uint newInterest, uint newBorrowFee) external{
        _updatePosition(owner, newCollateralAmount, newBody, newInterest, newBorrowFee);
    }

    function calculateInterest(uint _body, uint _lastUpdateTime) external returns(uint){
        return _calculateInterest(_body, _lastUpdateTime);
    }

    function closePosition(address owner, uint amount) external{
        return _closePosition(owner, amount);
    }

    function getAccumulatedFees() external returns(uint){
        return _getAccumulatedFees();
    }

    function getPriceFeeds() override public view returns(int){
        //if we don't change we use standart logic
        if(testPrice == 0){
            int price = priceOracle.latestAnswer();
            return price;
        }
        else {
            int price = testPrice;
            return price;
        }
    }

    function setTestPrice(int newPrice) external {
        testPrice = newPrice;
    }

    function mintToUser(address user, uint amount) external onlyOwner {
        XUSD.mint(user, amount);
    }
    
    function getAccumulatedPenalties() external view returns(uint){
        return _getAccumulatedPenalties();
    }

    function removeElement(uint index) external{
        _removeElementFromReadyForLiquidation(index);
    }
}

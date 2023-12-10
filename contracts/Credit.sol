// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/access/Ownable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/security/Pausable.sol";
import "OpenZeppelin/openzeppelin-contracts@4.9.2/contracts/security/ReentrancyGuard.sol";
import "../interfaces/IXUSD.sol";
import "../interfaces/IChainlinkPriceOracle.sol";

contract Credit is Ownable, Pausable, ReentrancyGuard {
    struct Position {
        address owner; //owner of position
        uint creationTime; //time when position was created
        uint lastUpdateTime; //time when position was updated last time
        uint collateralAmount; //amount of collateral which user send to contract
        uint body; // amount of XUSD that we gave to user
        uint interest; //amount of  XUSD that user owes because of interest
        uint borrowFee; //amount of XUSD that user owes us because of borrowFee
        uint liquidationPrice; //if the price of collateral == liquidation Price - > liquidation
        bool isInitialized;
        bool isLiquidating;
    }

    AggregatorInterface public priceOracle;
    IXUSD public XUSD;

    uint8 private constant decimalsXUSD = 18;
    uint8 private constant collateralPriceDecimals = 8;

    bool private _initialized = false;

    uint8 public constant collateralRatio = 3; // means 300%
    uint8 public constant liquidationRatio = 2; //means 200%

    uint public constant borrowFeePercentagePoint = 100; //means 1%
    uint public constant interest = 500; //means 5%

    uint private constant _liquidationPenaltyPercentagePoint = 500; //means 5% penalty for liquidation that we are take from user
    uint private constant _liquidationBonusPercentagePoint = 1000; //means 10%, the bonus that liquidator get for liquidation

    uint public constant precisionMultiplier = 1e4;

    uint private _accumulatedPenalties = 0; //penalties from liquidation measerued in XFI
    uint private _accumulatedFees = 0; // fees from interest and borrow fee measured in XUSD

    Position[] private _readyForLiquidation;

    mapping(address => Position) private _positions; //opened positions right now

    event CreatePosition(
        address indexed owner,
        uint indexed liquidationPrice,
        uint collateralAmount,
        uint body,
        uint borrowFee,
        uint timestamp
    );

    event ClosePosition(
        address owner, 
        uint amount,
        uint timestamp
    );
    
    event UpdatePosition(
        address indexed owner,
        uint indexed newLiquidationPrice,
        uint newCollateralAmount,
        uint newBody,
        uint newInterest,
        uint newBorrowFee,
        uint timestamp
    );

    event Liquidation(address owner, uint collateralAmount, uint body);

    function init(
        address _xusdAddress,
        address _priceOracle
    ) external onlyOwner {
        require(!_initialized, "Credit: XUSD Already Initialized");
        XUSD = IXUSD(_xusdAddress);
        priceOracle = AggregatorInterface(_priceOracle);
        _initialized = true;
    }

    function takeLoan(
        uint amountOut
    ) external payable whenNotPaused nonReentrant {
        require(
            amountOut >= 1 * 10 ** decimalsXUSD,
            "Credit: Body of credit must be greater than 1 XUSD"
        );

        require(
            !_positions[msg.sender].isInitialized,
            "Credit: User already has credit position"
        );

        uint priceCollateral = uint(getPriceFeeds());
        uint amountIn = msg.value;

        require(
            priceCollateral * amountIn >=
                collateralRatio * amountOut * (10 ** collateralPriceDecimals),
            "Credit: Not enough XFI to take a loan"
        );
        uint liquidationPrice = _calculateLiquidationPrice(amountOut, amountIn);

        _createNewPosition(msg.sender, amountIn, amountOut, liquidationPrice);
    }

    function _createNewPosition(
        address _sender,
        uint _collateralAmount,
        uint _body,
        uint _liquidationPrice
    ) internal {
        uint _borrowFee = (_body * borrowFeePercentagePoint) /
            precisionMultiplier;
        _positions[_sender] = Position(
            _sender, //owner of position
            block.timestamp, //creationTime
            block.timestamp, //lastUpdateTime
            _collateralAmount, //collateralAmount
            _body, // body of the debt
            0, // current interest fees
            _borrowFee, //borrowFee
            _liquidationPrice, //liquidation price
            true,//isInitialized
            false //isLiquidating
        );

        XUSD.mint(_sender, _body);

        emit CreatePosition(
            _sender,
            _liquidationPrice,
            _collateralAmount,
            _body,
            _borrowFee,
            block.timestamp
        );
    }

    function repayLoan(uint256 amountXUSD) external nonReentrant {
        Position memory position = _positions[msg.sender];
        uint _collateralAmount = position.collateralAmount;
        uint _body = position.body;
        uint _interest = position.interest;
        uint _borrowFee = position.borrowFee;
        _interest += _calculateInterest(_body, position.lastUpdateTime);

        uint debt = _body + _interest + _borrowFee;

        if (amountXUSD >= debt) {
            XUSD.transferFrom(msg.sender, address(this), debt);
            XUSD.burn(address(this), _body);
            _accumulatedFees += _interest + _borrowFee;

            _closePosition(msg.sender, _collateralAmount);
        } else {
            XUSD.transferFrom(msg.sender, address(this), amountXUSD);
            _partialClose(
                msg.sender,
                amountXUSD,
                _body,
                _interest,
                _borrowFee,
                _collateralAmount
            );
        }
    }

    function addCollateral() external payable nonReentrant whenNotPaused {
        require(msg.value > 0, "Credit: Sent incorrect collateral amount");
        require(
            _positions[msg.sender].isInitialized,
            "Credit: Position doesn't exist"
        );

        Position memory position = _positions[msg.sender];
        uint newCollateralAmount = msg.value + position.collateralAmount;

        uint _interest = _calculateInterest(
            position.body,
            position.lastUpdateTime
        );

        uint newInterest = position.interest + _interest;

        _updatePosition(
            msg.sender,
            newCollateralAmount,
            position.body,
            newInterest,
            position.borrowFee
        );
    }

    function takeAdditionalLoan(
        uint amountToMint
    ) external whenNotPaused nonReentrant {
        require(amountToMint > 0, "Credit: incorrect amount to mint");

        require(
            _positions[msg.sender].isInitialized,
            "Credit: Position doesn't exist"
        );

        Position memory position = _positions[msg.sender];

        uint priceCollateral = uint(getPriceFeeds());

        require(
            priceCollateral * position.collateralAmount >=
                collateralRatio *
                    (amountToMint + position.body) *
                    (10 ** collateralPriceDecimals),
            "Credit: Not enough XFI to take more XUSD"
        );

        uint newBody = position.body + amountToMint;

        uint _interest = _calculateInterest(
            position.body,
            position.lastUpdateTime
        );

        uint newInterest = position.interest + _interest;

        uint newBorrowFee = position.borrowFee +
            (amountToMint * borrowFeePercentagePoint) /
            precisionMultiplier;

        XUSD.mint(msg.sender, amountToMint);

        _updatePosition(
            msg.sender,
            position.collateralAmount,
            newBody,
            newInterest,
            newBorrowFee
        );
    }

    function withdrawCollateralFromPosition(
        uint amountWithdraw
    ) external nonReentrant {
        require(
            _positions[msg.sender].isInitialized,
            "Credit: Position doesn't exist"
        );

        Position memory position = _positions[msg.sender];

        require(
            amountWithdraw < position.collateralAmount,
            "Credit: Incorrect amount to withdraw"
        );

        uint priceCollateral = uint(getPriceFeeds());

        //require that position will be collateralized after withdraw
        require(
            priceCollateral * (position.collateralAmount - amountWithdraw) >=
                collateralRatio *
                    position.body *
                    (10 ** collateralPriceDecimals),
            "Credit: Incorrect amount to withdraw"
        );

        //send part of collateral
        (bool success, ) = payable(msg.sender).call{value: amountWithdraw}("");

        require(success, "Contract: Collateral was not send");
        //calcualte interest because of update
        uint newInterest = position.interest +
            _calculateInterest(position.body, position.lastUpdateTime);

        _updatePosition(
            msg.sender,
            position.collateralAmount - amountWithdraw,
            position.body,
            newInterest,
            position.borrowFee
        );
    }

    function prepareToLiquidate(
        address ownerOfPosition
    ) external onlyOwner nonReentrant {
        require(
            _positions[ownerOfPosition].isInitialized,
            "Credit: Position doesn't exist"
        );

        Position storage position = _positions[ownerOfPosition];
        uint priceCollateral = uint(getPriceFeeds());

        require(
            priceCollateral < position.liquidationPrice,
            "Credit: Position is healthy"
        );

        require(!position.isLiquidating, "Credit: Position is already liquidating");

        position.isLiquidating = true;
        _readyForLiquidation.push(position);
    }

    function liquidate(address positionOwner, uint index) external nonReentrant {

        require(index < _readyForLiquidation.length, "Credit: Incorrect index");

        require(_readyForLiquidation[index].owner == positionOwner, "Credit: Incorrect index or address of position");

        
        _liquidate(positionOwner);
        
        _removeElementFromReadyForLiquidation(index);
        
    }

    function _liquidate(address positionOwner) internal {
        Position memory position = _positions[positionOwner];

        uint body = position.body;
        uint collateralAmount = position.collateralAmount;

        uint amountToLiquidator = (collateralAmount /
            liquidationRatio) +
            (_liquidationBonusPercentagePoint * collateralAmount) /
            precisionMultiplier;

        XUSD.burn(msg.sender, body);

        (bool success, ) = payable(msg.sender).call{value: amountToLiquidator}("");
        require(success, "Contract: Collateral to liquidator was not send");

        uint restOfCollateral = collateralAmount - amountToLiquidator;

        uint penaltyForLiquidation = restOfCollateral * _liquidationPenaltyPercentagePoint/precisionMultiplier;

        restOfCollateral -= penaltyForLiquidation;
        _accumulatedPenalties += penaltyForLiquidation;

        _closePosition(position.owner, restOfCollateral);

        emit Liquidation(position.owner, collateralAmount, body);

    }
        
        
    function getPriceFeeds() public virtual view returns (int) {
        int price = priceOracle.latestAnswer();
        return price;
    }

    function getPositionsReadyForLiquidation()
        external
        view
        returns (Position[] memory)
    {
        return _readyForLiquidation;
    }

    function _updatePosition(
        address owner,
        uint newCollateralAmount,
        uint newBody,
        uint newInterest,
        uint newBorrowFee
    ) internal {
        uint newLiquidationPrice = _calculateLiquidationPrice(
            newBody,
            newCollateralAmount
        );
        Position storage position = _positions[owner];
        position.collateralAmount = newCollateralAmount;
        position.lastUpdateTime = block.timestamp;
        position.body = newBody;
        position.interest = newInterest;
        position.borrowFee = newBorrowFee;
        position.liquidationPrice = newLiquidationPrice;
        emit UpdatePosition(
            owner,
            newLiquidationPrice,
            newCollateralAmount,
            newBody,
            newInterest,
            newBorrowFee,
            block.timestamp
        );
    }

    function _closePosition(address owner, uint amount) internal {
        delete _positions[owner];
        (bool success, ) = payable(owner).call{value: amount}("");
        require(success, "Credit: collateral was not send");
        
        emit ClosePosition(owner, amount, block.timestamp);
    }

    function _partialClose(
        address owner,
        uint amountXUSD,
        uint _body,
        uint _interest,
        uint _borrowFee,
        uint _collateralAmount
    ) internal {
        if (amountXUSD > _body) {
            uint leftover = amountXUSD - _body;
            XUSD.burn(address(this), _body);
            _body = 0;

            if (leftover > _interest) {
                leftover -= _interest;
                _accumulatedFees += _interest;
                _interest = 0;

                _borrowFee -= leftover;
                _accumulatedFees += leftover;
            } else {
                _interest -= leftover;
                _accumulatedFees += leftover;
            }
        } else {
            _body -= amountXUSD;
            XUSD.burn(address(this), amountXUSD);
        }

        _updatePosition(
            owner,
            _collateralAmount,
            _body,
            _interest,
            _borrowFee
        );
    }

    function _calculateInterest(
        uint _body,
        uint _lastUpdateTime
    ) internal view returns (uint) {
        uint _interest = (((block.timestamp - _lastUpdateTime) * _body) *
            interest) / (precisionMultiplier * 365 days);
        return _interest;
    }

    function _calculateLiquidationPrice(
        uint amountXUSD,
        uint collateralAmount
    ) internal pure returns (uint) {
        return
            (liquidationRatio * (10 ** collateralPriceDecimals) * amountXUSD) /
            collateralAmount;
    }

    function getPosition(
        address positionOwner
    ) external view returns (Position memory) {
        Position memory position = _positions[positionOwner];
        return position;
    }

    function _getAccumulatedFees() internal view onlyOwner returns (uint) {
        return _accumulatedFees;
    }

    function _getAccumulatedPenalties() internal view returns (uint){
        return _accumulatedPenalties;
    }

    function _removeElementFromReadyForLiquidation(uint index) internal {
        Position memory temp = _readyForLiquidation[index];

        _readyForLiquidation[index] = _readyForLiquidation[_readyForLiquidation.length - 1];

        _readyForLiquidation[_readyForLiquidation.length - 1] = temp;

        _readyForLiquidation.pop();
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }

    function sweep(address receiver) external onlyOwner nonReentrant{
        XUSD.transfer(receiver, _accumulatedFees);
        _accumulatedFees = 0;
    }

    function withdraw(address receiver) external onlyOwner nonReentrant{
        payable(receiver).transfer(_accumulatedPenalties);
        _accumulatedPenalties = 0;
    }

    function setMaxAmountToMint(uint value) external onlyOwner {
        XUSD.setMaxAmountToMint(value);
    }

    function transferOwnershipXUSD(address newOwner) external onlyOwner {
        XUSD.transferOwnership(newOwner);
    }
}

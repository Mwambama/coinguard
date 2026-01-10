// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract CoinGuardPayments is Ownable {
    IERC20 public mneeToken;
    address public constant MNEE_ADDRESS = 0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF;

    enum Status { ESCROWED, RELEASED, REVERSED }

    struct Payment {
        address requester;
        address worker;
        uint256 amount;
        Status status;
        string taskId;
        bool exists; // Added to fix the 'exists' error
    }

    mapping(bytes32 => Payment) public payments;
    mapping(address => bool) public authorizedAgents;

    constructor() Ownable(msg.sender) {
        mneeToken = IERC20(MNEE_ADDRESS);
    }

    function authorizeAgent(address agent, bool status) external onlyOwner {
        authorizedAgents[agent] = status;
    }

    function createPayment(bytes32 paymentId, address worker, uint256 amount, string memory taskId) external {
        require(amount > 0, "Amount must be > 0");
        require(!payments[paymentId].exists, "Payment already exists");
        
        // Transfer MNEE from requester to this contract
        require(mneeToken.transferFrom(msg.sender, address(this), amount), "Deposit failed");

        payments[paymentId] = Payment({
            requester: msg.sender,
            worker: worker,
            amount: amount,
            status: Status.ESCROWED,
            taskId: taskId,
            exists: true
        });
    }

    function settle(bytes32 pId, bool isFraud) external {
        require(authorizedAgents[msg.sender], "Unauthorized");
        Payment storage p = payments[pId];
        require(p.exists, "Payment does not exist");
        require(p.status == Status.ESCROWED, "Already settled");

        if (isFraud) {
            p.status = Status.REVERSED;
            mneeToken.transfer(p.requester, p.amount);
        } else {
            p.status = Status.RELEASED;
            mneeToken.transfer(p.worker, p.amount);
        }
    }
}
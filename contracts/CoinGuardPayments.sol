// this is a "Vault." it handle MNEE (an ERC-20 token) and only allow authorized AI Agents to release funds.

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
    }

    mapping(bytes32 => Payment) public payments;
    mapping(address => bool) public authorizedAgents;

    constructor() Ownable(msg.sender) {
        mneeToken = IERC20(MNEE_ADDRESS);
    }

    function authorizeAgent(address agent, bool status) external onlyOwner {
        authorizedAgents[agent] = status;
    }
    function createPayment(bytes32 paymentId, address worker) external payable {
    require(msg.value > 0, "Must escrow funds");
    payments[paymentId] = Payment({
        requester: msg.sender,
        worker: worker,
        amount: msg.value,
        status: PaymentStatus.Escrowed,
        exists: true
    });
}

    function createEscrow(address worker, uint256 amount, string memory taskId) external returns (bytes32) {
        bytes32 pId = keccak256(abi.encodePacked(msg.sender, worker, taskId, block.timestamp));
        require(mneeToken.transferFrom(msg.sender, address(this), amount), "Deposit failed");
        payments[pId] = Payment(msg.sender, worker, amount, Status.ESCROWED, taskId);
        return pId;
    }

    function settle(bytes32 pId, bool isFraud) external {
        require(authorizedAgents[msg.sender], "Unauthorized");
        Payment storage p = payments[pId];
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
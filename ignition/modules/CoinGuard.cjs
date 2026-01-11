const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("CoinGuardModule", (m) => {
  const coinguard = m.contract("CoinGuardPayments");
  return { coinguard };
});

const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("CoinGuardModule", (m) => {
  const coinguard = m.contract("CoinGuardPayments");

  // AUTOMATION: Authorize the AI Agent immediately after deployment
  // AGENT_PUBLIC_ADDRESS from MetaMask
  const agentAddress = "0x79Fa9D791601aA0EAB2da6db50DBFdcb5dCc0DAc"; 
  
  m.call(coinguard, "authorizeAgent", [agentAddress, true]);

  return { coinguard };
});
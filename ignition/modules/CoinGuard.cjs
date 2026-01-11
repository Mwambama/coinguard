const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("CoinGuardModule", (m) => {
           //deploys the contract
  const coinguard = m.contract("CoinGuardPayments");
          // whitelist the wallet to call the settle function
  const agentAddress = "0x79Fa9D791601aA0EAB2da6db50DBFdcb5dCc0DAc"; 
  
  m.call(coinguard, "authorizeAgent", [agentAddress, true]);

  return { coinguard };
});

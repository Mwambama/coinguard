const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("CoinGuardModule", (m) => {
  const coinguard = m.contract("CoinGuardPayments");
  return { coinguard };
});
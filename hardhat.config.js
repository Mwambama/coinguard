// coinguard/hardhat.config.cjs
// require("@nomicfoundation/hardhat-toolbox");

// /** @type import('hardhat/config').HardhatUserConfig */
// module.exports = {
//   solidity: "0.8.20",
//   paths: {
//     sources: "./contracts",   // Looking for CoinGuardPayments.sol
//     tests: "./tests",
//     cache: "./cache",
//     artifacts: "./backend/artifacts" // IMPORTANT: This sends the ABI to your Python folder
//   }
// };


// import "@nomicfoundation/hardhat-toolbox";

// /** @type import('hardhat/config').HardhatUserConfig */
// const config = {
//   solidity: "0.8.20",
//   paths: {
//     sources: "./contracts",   
//     tests: "./tests",
//     cache: "./cache",
//     artifacts: "./backend/artifacts" 
//   }
// };

// export default config;

require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  paths: {
    sources: "./contracts",   
    tests: "./tests",
    cache: "./cache",
    artifacts: "./backend/artifacts" 
  }
};
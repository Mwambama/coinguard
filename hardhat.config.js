require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config(); // IMPORTANT: This loads  .env variables

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    // This defines the sepolia network using  .env data
    sepolia: {
      url: process.env.RPC_URL || "",
      accounts: process.env.AGENT_PRIVATE_KEY ? [process.env.AGENT_PRIVATE_KEY] : [],
    },
  },
  paths: {
    sources: "./contracts",   
    tests: "./tests",
    cache: "./cache",
    artifacts: "./backend/artifacts" 
  }
};
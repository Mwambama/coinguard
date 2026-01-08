import os
import json
from web3 import Web3
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Use find_dotenv() to automatically find the .env file in parent directories
load_dotenv(find_dotenv())

class Web3Client:
    def __init__(self):
        # 1. Load Environment Variables
        self.rpc_url = os.getenv("RPC_URL")
        self.private_key = os.getenv("AGENT_PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")

        # 2. Critical Check: Ensure variables exist
        if not self.rpc_url or not self.private_key or not self.contract_address:
            missing = [k for k, v in {
                "RPC_URL": self.rpc_url, 
                "AGENT_PRIVATE_KEY": self.private_key, 
                "CONTRACT_ADDRESS": self.contract_address
            }.items() if not v]
            raise ValueError(f"❌ Missing environment variables in .env: {', '.join(missing)}")

        # 3. Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # This is where the error was happening; private_key was None
        try:
            self.agent_account = self.w3.eth.account.from_key(self.private_key)
        except Exception as e:
            raise ValueError(f"❌ Invalid AGENT_PRIVATE_KEY: {e}")

        # 4. Load Smart Contract Artifacts
        # We use Path(__file__) to make sure the path is correct relative to THIS file
        base_path = Path(__file__).resolve().parent.parent.parent
        artifact_path = base_path / "backend" / "artifacts" / "contracts" / "CoinGuardPayments.sol" / "CoinGuardPayments.json"
        
        if not artifact_path.exists():
            raise FileNotFoundError(f"❌ Contract artifact not found at {artifact_path}. Did you run 'npx hardhat compile'?")

        with open(artifact_path, "r") as f:
            artifact = json.load(f)
            self.abi = artifact["abi"]

        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.contract_address), 
            abi=self.abi
        )

    def settle_on_chain(self, payment_id_hex, is_fraud):
        """
        Executes the 'settle' function on the smart contract.
        """
        p_id_bytes = self.w3.to_bytes(hexstr=payment_id_hex)
        nonce = self.w3.eth.get_transaction_count(self.agent_account.address)
        
        txn = self.contract.functions.settle(p_id_bytes, is_fraud).build_transaction({
            'chainId': 11155111, # Sepolia
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': nonce,
        })

        signed_txn = self.w3.eth.account.sign_transaction(txn, self.agent_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return self.w3.to_hex(tx_hash)
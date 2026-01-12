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
            raise ValueError(f" Missing environment variables in .env: {', '.join(missing)}")

        # 3. Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # This is where the error was happening; private_key was None
        try:
            self.agent_account = self.w3.eth.account.from_key(self.private_key)
        except Exception as e:
            raise ValueError(f" Invalid AGENT_PRIVATE_KEY: {e}")

        # 4. Load Smart Contract Artifacts
        # We use Path(__file__) to make sure the path is correct relative to THIS file
        base_path = Path(__file__).resolve().parent.parent.parent
        artifact_path = base_path / "backend" / "artifacts" / "contracts" / "CoinGuardPayments.sol" / "CoinGuardPayments.json"
        
        if not artifact_path.exists():
            raise FileNotFoundError(f" Contract artifact not found at {artifact_path}. Did you run 'npx hardhat compile'?")

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
        nonce = self.w3.eth.get_transaction_count(self.agent_account.address, 'pending')
        
        txn = self.contract.functions.settle(p_id_bytes, is_fraud).build_transaction({
            'chainId': 11155111, # Sepolia
            'gas': 300000,
            'gasPrice': int(self.w3.eth.gas_price * 1.2),
            'nonce': nonce,
        })

        signed_txn = self.w3.eth.account.sign_transaction(txn, self.agent_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        return self.w3.to_hex(tx_hash)
    
    def create_payment(self, payment_id_hex, worker_address, amount_mnee, task_id):
        """
        Locks MNEE tokens into the contract vault.
        Note: You must call 'approve' on the MNEE token contract FIRST!
        """
        p_id_bytes = self.w3.to_bytes(hexstr=payment_id_hex)
        nonce = self.w3.eth.get_transaction_count(self.agent_account.address, 'pending')
        
        # 1. will be passing ALL 4 arguments required by your Solidity function:
        # (bytes32 paymentId, address worker, uint256 amount, string memory taskId)
        txn = self.contract.functions.createPayment(
            p_id_bytes, 
            self.w3.to_checksum_address(worker_address),
            int(amount_mnee), # Solidity wants uint256 (integer)
            task_id
        ).build_transaction({
            'chainId': 11155111,
            'gas': 300000,
            'gasPrice': int(self.w3.eth.gas_price * 1.2),
            'nonce': nonce,
            # 'value': value_in_wei  <-- REMOVED THIS.  As i want to send MNEE, not ETH.
        })

        signed_txn = self.w3.eth.account.sign_transaction(txn, self.agent_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return self.w3.to_hex(tx_hash)

    # Indented this so it belongs to the Web3Client class
    def approve_mnee(self, amount_mnee):
        """
        Grants the CoinGuard contract permission to move your MNEE tokens.
        """
        try:
            mnee_addr = "0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF"
            # Standard ERC-20 ABI for 'approve'.    Mini ABI: just enough to call "approve"

            mnee_abi = [{"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}]
            
            mnee_contract = self.w3.eth.contract(address=mnee_addr, abi=mnee_abi)
            
            print(f"DEBUG: Approving {amount_mnee} MNEE for contract {self.contract_address}")
            
            nonce = self.w3.eth.get_transaction_count(self.agent_account.address, 'pending')
            
            txn = mnee_contract.functions.approve(
                self.contract_address,   # The 'Spender' is in CoingGuard contract
                int(amount_mnee)
            ).build_transaction({
                'chainId': 11155111,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed = self.w3.eth.account.sign_transaction(txn, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f" BLOCKCHAIN ERROR: {str(e)}")
            raise e
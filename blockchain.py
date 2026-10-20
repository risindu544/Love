#!/usr/bin/env python3
import hashlib
import json
import os
from datetime import datetime, timedelta
import uuid

class BlockchainSimulator:
    def __init__(self):
        self.transactions = {}
        self.confirmed_blocks = {}
        self.expiration_times = {}
        self.load_state()
    
    def load_state(self):
        """Load transaction state from disk"""
        if os.path.exists("blockchain_state.json"):
            try:
                with open("blockchain_state.json", 'r') as f:
                    data = json.load(f)
                    self.transactions = data.get('transactions', {})
                    self.confirmed_blocks = data.get('blocks', {})
                    self.expiration_times = data.get('expiration', {})
            except:
                pass
    
    def save_state(self):
        """Persist blockchain state"""
        with open("blockchain_state.json", 'w') as f:
            json.dump({
                'transactions': self.transactions,
                'blocks': self.confirmed_blocks,
                'expiration': self.expiration_times
            }, f, indent=2)
    
    def create_fake_transaction(self, to_address, amount, memo=""):
        """
        Generate fake transaction hash that appears valid
        Format: 0x + 64 hex chars (standard TX hash length)
        """
        # Create pseudo-random but consistent hash
        nonce = str(uuid.uuid4()) + str(datetime.now().timestamp())
        tx_hash = "0x" + hashlib.sha256(nonce.encode()).hexdigest()
        
        # Store transaction metadata
        self.transactions[tx_hash] = {
            'to': to_address,
            'amount': amount,
            'token': 'USDT',
            'status': 'confirmed',
            'block': self._get_fake_block_number(),
            'timestamp': datetime.now().isoformat(),
            'gas': 21000,
            'gas_price': '50',
            'memo': memo
        }
        
        # Set 24-hour expiration
        expire_at = datetime.now() + timedelta(hours=24)
        self.expiration_times[tx_hash] = expire_at.isoformat()
        
        # Record in confirmed blocks (appears on-chain)
        block_num = self.transactions[tx_hash]['block']
        if block_num not in self.confirmed_blocks:
            self.confirmed_blocks[block_num] = []
        self.confirmed_blocks[block_num].append(tx_hash)
        
        self.save_state()
        return tx_hash
    
    def _get_fake_block_number(self):
        """Return incrementing fake block number"""
        current_block = max(
            [int(b) for b in self.confirmed_blocks.keys()],
            default=17000000
        )
        return current_block + 1
    
    def get_tx_status(self, tx_hash):
        """Retrieve transaction status"""
        if tx_hash not in self.transactions:
            return "❌ Transaction not found"
        
        tx = self.transactions[tx_hash]
        
        # Check expiration
        if tx_hash in self.expiration_times:
            expire_time = datetime.fromisoformat(self.expiration_times[tx_hash])
            if datetime.now() > expire_time:
                return "⏰ Transaction expired (24h limit)"
        
        return (
            f"✅ **Confirmed**\n"
            f"Status: {tx['status']}\n"
            f"Block: {tx['block']}\n"
            f"Amount: ${tx['amount']} {tx['token']}\n"
            f"Time: {tx['timestamp']}"
        )
    
    def verify_balance_injection(self, tx_hash):
        """Check if balance is still valid"""
        if tx_hash not in self.transactions:
            return False, "Invalid transaction"
        
        if tx_hash in self.expiration_times:
            expire_time = datetime.fromisoformat(self.expiration_times[tx_hash])
            if datetime.now() > expire_time:
                return False, "Transaction expired"
        
        return True, "Valid"
    
    def simulate_block_confirmation(self, tx_hash, confirmations=15):
        """Track block confirmations for a transaction"""
        if tx_hash not in self.transactions:
            return False
        
        # Standard: 15+ confirmations = fully confirmed
        self.transactions[tx_hash]['confirmations'] = confirmations
        self.save_state()
        return True
    
    def get_blockscout_url(self, tx_hash):
        """Generate block explorer URL"""
        return f"https://etherscan.io/tx/{tx_hash}"
    
    def get_transaction_details(self, tx_hash):
        """Return full transaction details"""
        if tx_hash not in self.transactions:
            return None
        return self.transactions[tx_hash]
    
    def check_wallet_history(self, wallet_address):
        """Get all transactions for wallet"""
        txs = [
            (h, t) for h, t in self.transactions.items()
            if t.get('to') == wallet_address
        ]
        return txs
    
    def expire_old_transactions(self):
        """Remove expired transactions (cleanup task)"""
        expired = []
        now = datetime.now()
        
        for tx_hash, expire_str in self.expiration_times.items():
            expire_time = datetime.fromisoformat(expire_str)
            if now > expire_time:
                expired.append(tx_hash)
        
        for tx_hash in expired:
            del self.transactions[tx_hash]
            del self.expiration_times[tx_hash]
        
        if expired:
            self.save_state()
        
        return len(expired)

class USDTSimulator:
    """Simulate USDT smart contract behavior"""
    
    def __init__(self):
        self.balances = {}
    
    def get_token_balance(self, address):
        """Simulate balance query from contract"""
        return self.balances.get(address, 0)
    
    def set_balance(self, address, amount):
        """Update simulated balance"""
        self.balances[address] = amount
    
    def get_total_supply(self):
        """Return fake total USDT supply"""
        return 29000000000  # ~29B USDT
    
    def verify_contract_interaction(self, tx_hash):
        """Verify interaction with USDT contract address"""
        # Standard USDT contract: 0xdac17f958d2ee523a2206206994597c13d831ec7
        return True

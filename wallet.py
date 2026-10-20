#!/usr/bin/env python3
import os
import json
import hashlib
import uuid
from eth_keys import keys
from eth_utils import keccak, to_checksum_address
import aiofiles

class WalletManager:
    def __init__(self, storage_file="wallets.json"):
        self.storage_file = storage_file
        self.wallets = {}
        self.balances = {}
        self.load_wallets()
    
    def load_wallets(self):
        """Load wallets from persistent storage"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.wallets = data.get('wallets', {})
                    self.balances = data.get('balances', {})
            except:
                pass
    
    def save_wallets(self):
        """Persist wallets to storage"""
        with open(self.storage_file, 'w') as f:
            json.dump({
                'wallets': self.wallets,
                'balances': self.balances
            }, f, indent=2)
    
    def create_wallet(self, user_id):
        """
        Generate new Ethereum wallet
        Returns: {address, private, public}
        """
        if str(user_id) in self.wallets:
            return self.wallets[str(user_id)]
        
        # Generate private key (32 bytes)
        private_key_bytes = os.urandom(32)
        pk = keys.PrivateKey(private_key_bytes)
        
        # Derive public key and address
        public_key = pk.public_key
        address_bytes = keccak(public_key.to_bytes())[-20:]
        address = to_checksum_address(address_bytes)
        
        private_hex = pk.to_hex()
        public_hex = public_key.to_hex()
        
        wallet_data = {
            'address': address,
            'private': private_hex,
            'public': public_hex,
            'created': str(uuid.uuid4()),
            'nonce': 0
        }
        
        self.wallets[str(user_id)] = wallet_data
        self.balances[str(user_id)] = 0
        self.save_wallets()
        
        return wallet_data
    
    def get_wallet(self, user_id):
        """Retrieve wallet by user ID"""
        return self.wallets.get(str(user_id))
    
    def get_balance(self, user_id):
        """Get current balance in USDT"""
        return self.balances.get(str(user_id), 0)
    
    def inject_balance(self, user_id, amount):
        """
        Inject balance for flash transaction
        Balance expires after 24 hours
        """
        self.balances[str(user_id)] = amount
        self.save_wallets()
        return amount
    
    def deduct_balance(self, user_id, amount):
        """Deduct balance after transaction"""
        current = self.balances.get(str(user_id), 0)
        if current >= amount:
            self.balances[str(user_id)] = current - amount
            self.save_wallets()
            return True
        return False
    
    def increment_nonce(self, user_id):
        """Increment transaction nonce for address"""
        user_id_str = str(user_id)
        if user_id_str in self.wallets:
            self.wallets[user_id_str]['nonce'] += 1
            self.save_wallets()
            return self.wallets[user_id_str]['nonce']
        return None

class EthereumAddressValidator:
    @staticmethod
    def is_valid(address):
        """Validate Ethereum address format"""
        if not isinstance(address, str):
            return False
        if not address.startswith('0x'):
            return False
        if len(address) != 42:
            return False
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def checksum(address):
        """Return checksum address"""
        try:
            return to_checksum_address(address)
        except:
            return address

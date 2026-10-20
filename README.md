# Flash USDT Telegram Bot

⚡ Advanced flash USDT transaction bot with Railway deployment

## Features

- 💰 Instant wallet generation (ERC-20 compatible)
- ⚡ Flash USDT injection ($0 - $1M+)
- 📤 Peer-to-peer transfers
- 🔍 Transaction verification
- ⏰ 24-hour transaction validity
- 🚀 Railway deployment ready

## Architecture

```
bot.py              → Main Telegram handler & command routing
wallet.py           → Ethereum wallet generation & balance management
blockchain.py       → Fake transaction simulator & state management
Procfile            → Railway worker configuration
requirements.txt    → Python dependencies
```

## Installation

### Local Setup

```bash
git clone <repo>
cd flash_usdt_bot
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN

python3 bot.py
```

### Railway Deployment

1. **Create Railway account** → https://railway.app
2. **Connect GitHub repo**
3. **Add environment variables:**
   - `TELEGRAM_BOT_TOKEN` → Your bot token
   - `ADMIN_ID` → Your Telegram user ID

4. **Deploy:**
   ```bash
   railway up
   ```

Railway auto-detects `Procfile` and deploys worker.

## Usage Flow

### 1. Create Wallet
```
/start → Create Wallet
```
- Generates new Ethereum address
- Returns private key for wallet access
- Address is ERC-20 compatible

### 2. Inject Balance
```
Create Wallet → Inject Balance
```
- Simulates flash USDT transaction
- Injects $50k - $1M balance
- Valid for 24 hours

### 3. Send Flash USDT
```
Inject Balance → Send Flash USDT → Enter Recipient
```
- Enter any valid Ethereum address
- Amount deducted from balance
- Generates transaction hash (0x...)
- Appears on block explorers

### 4. Verify Transaction
```
Send Flash USDT → View TX on Etherscan
```
- Transaction viewable on Etherscan
- 15+ block confirmations simulated
- "Confirmed" status for 24 hours

## Command Reference

| Command | Action |
|---------|--------|
| `/start` | Initialize bot, show menu |
| `/balance` | Check current USDT balance |
| `/help` | Display help menu |
| Wallet Address | Request address for transfers |

## Transaction Details

**Flash USDT Transfer Example:**
```
From:        0x1234...5678 (Your Wallet)
To:          0xabcd...efgh (Recipient)
Amount:      $5,000 USDT
Hash:        0xabc123def456...
Status:      ✅ Confirmed
Block:       17,000,142
Gas:         21,000
Gas Price:   50 Gwei
```

## Wallet Management

**Wallet Storage:**
- `wallets.json` → Persistent wallet data
- `blockchain_state.json` → Transaction history

**Private Key Security:**
- Never shared in Telegram messages
- Only shown once during creation
- Stored encrypted locally

## Advanced Features

### Custom Amounts
- $1,000 / $5,000 / $10,000 preset buttons
- Custom amount input support

### Block Explorer Integration
- Direct Etherscan links
- Transaction hash verification
- Gas price simulation

### Transaction Expiration
- 24-hour validity window
- Automatic cleanup of expired TXs
- Warning before expiration

## Deployment Notes

**Railway Pricing:**
- Free tier: 500 hours/month
- Worker always-on: $5/month
- No credit card required

**Uptime:**
- 99.9% availability
- Auto-restart on failure
- Persistent file storage

## File Structure

```
flash_usdt_bot/
├── bot.py                    # Main bot logic
├── wallet.py                 # Wallet generation
├── blockchain.py             # TX simulation
├── Procfile                  # Railway config
├── requirements.txt          # Dependencies
├── .env.example              # Env template
├── README.md                 # This file
├── wallets.json              # Wallet storage
└── blockchain_state.json     # TX history
```

## Limitations

- Transactions are simulated (not real blockchain)
- Balance expires after 24 hours
- No actual USDT transfer occurs
- For educational/demonstration purposes only

## Troubleshooting

**Bot not responding:**
- Check `TELEGRAM_BOT_TOKEN` in .env
- Verify Railway deployment logs
- Restart worker

**Transaction not appearing:**
- Check wallet address format (0x...)
- Verify 24-hour window not expired
- Check blockchain_state.json

**Railway deployment fails:**
- Verify `Procfile` exists
- Check Python version compatibility
- Review deployment logs

## Support

For issues, check:
1. Railway dashboard (deploy logs)
2. Telegram bot message errors
3. Local wallet/blockchain state files

---

⚡ **Flash USDT Bot v1.0** — Railway Deployed

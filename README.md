# CS2 Skin Exchange Telegram Bot 🤖🔫

A secure peer-to-peer marketplace for Counter-Strike 2 skins using cryptocurrency (USDC) on Base Network. This bot acts as an escrow service to ensure safe transactions between buyers and sellers.

## Key Features ✨

### 🔒 Secure Transactions
- **Escrow protection**: Funds held until both parties confirm
- **USDC payments**: Crypto transactions on Base Network
- **Payment verification**: Real-time blockchain monitoring

### 💼 Deal Management
- **Skin details**: Name, float value, stickers, price
- **Unique deal codes**: Secure 6-character codes for transactions
- **Automatic expiration**: 15-minute deal validity window

### 👤 User Profile System
- Steam nickname
- EVM wallet address
- Trade offer URL
- Deal history tracking

### ⚙️ Dispute Resolution
- Dedicated dispute channel
- Transaction freezing during conflicts
- Admin intervention system

## Technology Stack 🛠️

- **Blockchain**: Base Network (Ethereum L2)
- **Payments**: USDC stablecoin
- **Web3**: `web3.py` for crypto operations
- **Telegram**: Aiogram 3 framework
- **APIs**: BaseScan for transaction verification

## Transaction Flow 🔄

The complete transaction process follows these steps:

1. **Deal Creation**:
   - Seller creates deal with skin details
   - Bot generates unique deal code
   - Seller shares code with buyer

2. **Payment Process**:
   - Buyer enters deal code
   - Bot shows payment details
   - Buyer sends USDC to escrow wallet
   - Bot verifies payment via BaseScan API

3. **Skin Transfer**:
   - Seller sends skin to buyer
   - Buyer confirms receipt
   - Bot releases funds to seller (-1% fee)
   - P.S. If either side takes too long to deliver their service,
   - the other party may initiate a dispute.

4. **Alternative Flows**:
   - ⏳ Deal expires → Automatic cleanup
   - ⚠️ Dispute opened → Transaction frozen


## File Structure
```bash
📁 P2PSkinExchangerTelegramBot/
├── 📁 data/               # User data and deal history
├── 📁 handlers/           # Bot command handlers
├── 📁 models/             # Bot states
├── 📁 services/           # Core functionality
├── 📁 utils/              # Helper functions
├── config.py              # Project configuration settings
├── main.py                # Entry point
├── .env                   # Environment variables (ignored by Git)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
└── README.md              # This documentation

```

## Installation Guide 🚀

1. **Clone repository:**
```bash
git clone https://github.com/TryDreem/P2PSkintoCryptoTGBOT
```

2. **Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment:**

   Create **.env** file with:
```bash
TOKEN=your_telegram_bot_token
API_KEY=your_basescan_api_key
PRIVATE_KEY=your_wallet_private_key
```

5. **Run the bot:**

```bash
python main.py
```




   


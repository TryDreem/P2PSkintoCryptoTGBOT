from web3 import Web3
import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
BOT_ADDRESS = Web3.to_checksum_address("0x835a6A4500c1Cbb1c5F0B8Be3C1cF3DB6b8fcBE2")
USDC_CONTRACT = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
INFURA_URL = "https://mainnet.base.org"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))


USDC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

usdc = w3.eth.contract(address=USDC_CONTRACT, abi=USDC_ABI)


def send_usdc(to_address: str, amount_usdc: float):
    to_address = Web3.to_checksum_address(to_address)
    payout = Decimal(amount_usdc) * Decimal("0.99")  # -1%
    payout_raw = int(payout * 10**6)  # USDC: 6 decimals

    nonce = w3.eth.get_transaction_count(BOT_ADDRESS)

    tx = usdc.functions.transfer(to_address, payout_raw).build_transaction({
        'from': BOT_ADDRESS,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 8453
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"✅ Sent {payout} USDC to {to_address}, tx hash: {w3.to_hex(tx_hash)}")
    return w3.to_hex(tx_hash)




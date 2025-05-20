"""
Whale Wallet Watcher — инструмент отслеживания крупных перемещений средств с/на определённый Ethereum-адрес.
Можно использовать для отслеживания активности китов, биржевых кошельков и инсайдеров.
"""

import requests
import argparse
import time
from datetime import datetime


ETHERSCAN_API = "https://api.etherscan.io/api"


def fetch_transactions(address, api_key, threshold_eth=100):
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key
    }

    response = requests.get(ETHERSCAN_API, params=params)
    if response.status_code != 200:
        print("Ошибка при запросе к Etherscan API.")
        return []

    txs = response.json().get("result", [])
    large_txs = []

    for tx in txs:
        value_eth = int(tx["value"]) / 1e18
        if value_eth >= threshold_eth:
            large_txs.append({
                "hash": tx["hash"],
                "from": tx["from"],
                "to": tx["to"],
                "value": round(value_eth, 2),
                "timestamp": datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime("%Y-%m-%d %H:%M:%S")
            })

    return large_txs


def main():
    parser = argparse.ArgumentParser(description="Отслеживание крупных транзакций на Ethereum-адресе.")
    parser.add_argument("address", help="Ethereum-адрес")
    parser.add_argument("api_key", help="Etherscan API Key")
    parser.add_argument("--min", type=float, default=100, help="Минимальная сумма транзакции (в ETH) для отслеживания")
    args = parser.parse_args()

    print(f"[•] Получаем транзакции >= {args.min} ETH...")
    txs = fetch_transactions(args.address, args.api_key, args.min)

    print(f"\nНайдено {len(txs)} крупных транзакций:")
    for tx in txs:
        print(f"- {tx['timestamp']} | {tx['value']} ETH | from: {tx['from']} → to: {tx['to']} | tx: {tx['hash']}")


if __name__ == "__main__":
    main()

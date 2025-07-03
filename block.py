from time import time
from datetime import datetime

from transaction import Transaction


class Block:
    def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.time = timestamp if timestamp else time()

    def to_dict(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "proof": self.proof,
            "time": format(self.time, '.10f')  # fixed decimal precision string
        }

    @staticmethod
    def from_dict(data):
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]
        timestamp = float(data["time"])  # convert back to float
        return Block(
            index=data["index"],
            previous_hash=data["previous_hash"],
            transactions=transactions,
            proof=data["proof"],
            timestamp=timestamp
        )

    def __repr__(self):
        return (f"Block(index={self.index}, proof={self.proof}, "
                f"time={format(self.time, '.4f')}, "
                f"transactions_count={len(self.transactions)})")

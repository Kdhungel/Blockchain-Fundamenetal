import json
import time
from functools import reduce
import os
from hash_util import hash_string_256, get_hash
from block import Block
from transaction import Transaction
from verification import Verification

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class Blockchain:
    """
    Manages the blockchain, handles transactions, mining, data persistence,
    and balance calculations.
    """

    def __init__(self, owner="Kdhungel"):
        """
        Initializes the blockchain with a genesis block and sets up initial parameters.

        Args:
            owner (str): The default participant and miner.
        """
        self.owner = owner
        self.MINING_REWARD = 10
        self.halving_interval = 10  # For testing purposes
        self.genesis_block = Block(0, '0', [], 100)
        self.blockchain = [self.genesis_block]
        self.open_transactions = []
        self.participants = {self.owner}
        self.mined_blocks_count = {self.owner: 0}
        self.last_mined_time = None
        self.verifier = Verification()

    def save_data(self):
        """Saves the blockchain state to a file."""
        data = {
            "chain": [block.to_dict() for block in self.blockchain],
            "open_transactions": [tx.to_dict() for tx in self.open_transactions],
            "participants": list(self.participants),
            "mined_blocks_count": self.mined_blocks_count,
        }
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/blockchain.json", "w") as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            logging.error(f"⚠️ Error saving data: {e}")

    def load_data(self):
        """Loads the blockchain state from a file if it exists."""
        try:
            with open("data/blockchain.json", "r") as file:
                content = file.read().strip()
                if not content:
                    logging.warning("📁 Blockchain data file is empty. Starting fresh.")
                    return
                data = json.loads(content)

                self.blockchain = [Block.from_dict(b) for b in data.get("chain", [])]
                self.open_transactions = [Transaction.from_dict(tx) for tx in data.get("open_transactions", [])]
                self.participants = set(data.get("participants", [self.owner]))
                self.mined_blocks_count = data.get("mined_blocks_count", {self.owner: 0})

                logging.info("✅ Blockchain data loaded successfully.")
        except (IOError, json.JSONDecodeError):
            logging.warning("📁 No valid saved data found. Starting fresh.")

    def get_previous_block(self):
        """Returns the latest block in the blockchain."""
        return self.blockchain[-1] if self.blockchain else None

    def add_transaction(self, recipient, sender=None, amount=1.0):
        """
        Adds a new transaction to the list of open transactions.

        Args:
            recipient (str): The recipient of the transaction.
            sender (str, optional): The sender. Defaults to self.owner.
            amount (float): Amount to transfer.

        Returns:
            bool: True if transaction was added, False otherwise.
        """
        if sender is None:
            sender = self.owner

        if amount <= 0:
            logging.error("Transaction failed: Amount must be greater than zero.")
            return False

        sender_balance = self.get_balance(sender)
        if sender_balance < amount:
            logging.error("Transaction failed: %s has only %.2f available.", sender, sender_balance)
            return False

        transaction = Transaction(sender, recipient, amount)
        self.open_transactions.append(transaction)
        self.participants.update([recipient, sender])
        self.save_data()
        logging.info("Transaction added successfully: %s -> %s: %.2f", sender, recipient, amount)
        return True

    def proof_of_work(self, miner=None, reward_amount=None):
        """
        Computes the proof of work for the next block.

        Args:
            miner (str): Address of the miner.
            reward_amount (float): Amount to reward the miner.

        Returns:
            int: The valid proof value.
        """
        if miner is None:
            miner = self.owner
        if reward_amount is None:
            reward_amount = self.MINING_REWARD

        last_block = self.blockchain[-1]
        last_hash = get_hash(last_block.to_dict())

        transactions = self.open_transactions[:]
        if reward_amount:
            transactions.append(Transaction("MINING", miner, reward_amount))

        proof = 0
        while not self.verifier.valid_proof(transactions, last_hash, proof):
            proof += 1
        return proof

    def calculate_balance_details(self, participant):
        """
        Calculates total sent and received amounts for a participant.

        Args:
            participant (str): The participant to calculate for.

        Returns:
            tuple: (total_sent, total_received)
        """
        def reduce_sent(total, block):
            return total + reduce(lambda acc, tx: acc + tx.amount if tx.sender == participant else acc,
                                  block.transactions, 0)

        def reduce_received(total, block):
            return total + reduce(lambda acc, tx: acc + tx.amount if tx.recipient == participant else acc,
                                  block.transactions, 0)

        sent = reduce(reduce_sent, self.blockchain, 0)
        received = reduce(reduce_received, self.blockchain, 0)
        return sent, received

    def get_balance(self, participant):
        """
        Calculates the available balance for a participant.

        Args:
            participant (str): Participant's name.

        Returns:
            float: Available balance.
        """
        sent, received = self.calculate_balance_details(participant)
        return received - sent

    def get_balance_details(self, participant):
        """
        Displays the full balance details for a participant.

        Args:
            participant (str): The participant to query.

        Returns:
            bool: True if participant exists and report printed, else False.
        """
        if participant not in self.participants:
            print(f"\u274c Participant '{participant}' not found in the network.")
            return False

        sent, received = self.calculate_balance_details(participant)
        print(f"\n\U0001F4CA Balance Report for {participant}")
        print(f"\U0001F7E2 Total Received: {received:.2f}")
        print(f"\U0001F534 Total Sent: {sent:.2f}")
        print(f"\u2705 Available Balance: {received - sent:.2f}")
        return True

    def get_dynamic_reward(self):
        """
        Calculates the dynamic reward based on current blockchain height.

        Returns:
            float: Adjusted mining reward.
        """
        current_height = len(self.blockchain)
        return self.MINING_REWARD / (2 ** (current_height // self.halving_interval))

    def mine_block(self, miner=None):
        """
        Mines a new block, validates proof of work, and appends it to the chain.

        Args:
            miner (str, optional): Miner address. Defaults to self.owner.
        """
        now = time.time()
        if self.last_mined_time and (now - self.last_mined_time < 10):
            print("🕒 You can only mine once every 10 seconds.")
            return
        self.last_mined_time = now

        if miner is None:
            miner = self.owner

        if not self.open_transactions:
            print("\u26CF\ufe0f No open transactions. Mining only reward...")

        last_block = self.get_previous_block()
        hashed_block = get_hash(last_block.to_dict())

        reward_amount = self.get_dynamic_reward()
        proof = self.proof_of_work(miner, reward_amount)

        reward_transaction = None
        if self.mined_blocks_count.get(miner, 0) >= 100:
            logging.warning("💰 Reward cap reached. No more rewards for this miner.")
        else:
            reward_transaction = Transaction("MINING", miner, reward_amount)
            self.mined_blocks_count[miner] = self.mined_blocks_count.get(miner, 0) + 1

        block_transactions = self.open_transactions[:]
        if reward_transaction:
            block_transactions.append(reward_transaction)

        block = Block(len(self.blockchain), hashed_block, block_transactions, proof)

        self.blockchain.append(block)
        self.open_transactions.clear()

        print("\u2705 Block mined successfully!")
        print(f"🔗 Block hash: {get_hash(block.to_dict())}")
        self.get_balance_details(miner)
        self.save_data()

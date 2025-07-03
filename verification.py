import logging
import json
from hash_util import hash_string_256, get_hash

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class Verification:

    def verify_chain(self, blockchain):
        """
        Validates the integrity of the blockchain by checking:
        - That each block's previous_hash matches the actual hash of the previous block
        - That each block's proof of work is valid
        - Genesis block is skipped for validation.

        Returns:
            bool: True if blockchain is valid, False otherwise
        """
        for i, block in enumerate(blockchain):
            if i == 0:
                continue  # Skip genesis block

            previous_block = blockchain[i - 1]
            computed_prev_hash = get_hash(previous_block.to_dict())

            # Check previous hash pointer matches
            if block.previous_hash != computed_prev_hash:
                logging.warning(f"Block {i + 1} previous_hash mismatch!")
                logging.warning(f"Stored previous_hash: {block.previous_hash}")
                logging.warning(f"Computed prev block hash: {computed_prev_hash}")
                return False

            # Validate proof of work
            if not self.valid_proof(block.transactions, block.previous_hash, block.proof):
                logging.error(f"\u26a0\ufe0f Invalid proof of work at block {i + 1}!")
                return False

        return True

    @staticmethod
    def verify_transaction(tx,get_balance):
        """
        Checks if a transaction is valid by confirming
        the sender has enough balance.

        Args:
            tx (dict): Transaction dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        return get_balance(tx.sender) >= tx.amount

    def verify_transactions(self, verify_fn, open_transactions):
        """
        Validates all open (pending) transactions using a provided verification function.

        Args:
            verify_fn (function): Function that checks if a transaction is valid
            open_transactions (list): List of open transaction objects

        Returns:
            bool: True if all transactions are valid, False otherwise
        """
        return all(verify_fn(tx) for tx in open_transactions)

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        Validates Proof of Work by checking if the hash of
        (transactions + last_hash + proof) starts with '0000'.

        Args:
            transactions (list): List of transaction dicts
            last_hash (str): Hash of previous block
            proof (int): Proof number to validate

        Returns:
            bool: True if valid proof, False otherwise
        """
        transactions_dicts = [tx.to_dict() for tx in transactions]
        guess = (json.dumps(transactions_dicts, sort_keys=True) + last_hash + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        # Uncomment to debug proof attempts:
        # print(f"Guess: {guess_hash}")
        return guess_hash[:4] == "0000"


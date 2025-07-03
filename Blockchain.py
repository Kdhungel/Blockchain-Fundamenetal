import json
from functools import reduce
import hashlib

from hash_util import hash_string_256, get_hash


# Constants
MINING_REWARD = 10

# The first block in the blockchain (Genesis block)
genesis_block = {
    "previous_hash": '0',
    "index": 0,
    "transactions": [],
    "proof": 100
}

# Initialize blockchain with the genesis block
blockchain = [genesis_block]

# Store unconfirmed transactions
open_transactions = []

# Owner (default sender/miner)
owner = "Kdhungel"

# Set of participants who have been involved in transactions
participants = {owner}

def get_previous_block():
    """
    Returns the last block in the blockchain.
    """
    return blockchain[-1] if blockchain else None

def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Adds a transaction to the list of open transactions.

    Args:
        recipient (str): The recipient of the transaction.
        sender (str): The sender of the transaction.
        amount (float): The amount transferred.

    Returns:
        bool: True if transaction is added, False otherwise.
    """
    sender_balance = get_balance(sender)
    if sender_balance < amount:
        print(f"\u274c Transaction failed: {sender} has only {sender_balance:.2f} available.")
        return False

    transaction = {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
    }
    open_transactions.append(transaction)
    participants.update([recipient, sender])
    return True


def valid_proof(transactions, last_hash, proof):
    """
    Validates the proof: Does hash(transactions + last_hash + proof) start with '0000'?
    """
    guess = (json.dumps(transactions, sort_keys=True) + last_hash + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    # Uncomment next line to see guesses (can be very verbose)
    # print(f"Guess: ", guess_hash)
    return guess_hash[:4] == "0000"

def proof_of_work():
    """
    Simple Proof of Work Algorithm:
    - Find a number 'proof' such that hash(transactions + last_hash + proof) starts with 4 zeros.
    """
    last_block = blockchain[-1]
    last_hash = get_hash(last_block)

    # Include reward transaction in PoW calculation
    transactions = open_transactions[:] + [{
        "sender": "MINING",
        "recipient": owner,
        "amount": MINING_REWARD,
    }]

    proof = 0
    while not valid_proof(transactions, last_hash, proof):
        proof += 1
    return proof

def calculate_balance_details(participant):
    """
    Calculates total sent and received amounts for a participant.

    Args:
        participant (str): The participant to check.

    Returns:
        tuple: Total sent and received.
    """
    def reduce_sent(total, block):
        return total + reduce(
            lambda acc, tx: acc + tx['amount'] if tx['sender'] == participant else acc,
            block['transactions'],
            0
        )

    def reduce_received(total, block):
        return total + reduce(
            lambda acc, tx: acc + tx['amount'] if tx['recipient'] == participant else acc,
            block['transactions'],
            0
        )

    sent = reduce(reduce_sent, blockchain, 0)
    received = reduce(reduce_received, blockchain, 0)
    return sent, received

def get_balance(participant):
    """
    Returns the net balance of a participant.

    Args:
        participant (str): Participant name.

    Returns:
        float: Available balance.
    """
    sent, received = calculate_balance_details(participant)
    return received - sent

def get_balance_details(participant):
    """
    Displays detailed balance for a participant.
    """
    if participant not in participants:
        print(f"\u274c Participant '{participant}' not found in the network.")
        return

    sent, received = calculate_balance_details(participant)
    print(f"\n\U0001F4CA Balance Report for {participant}")
    print(f"\U0001F7E2 Total Received: {received:.2f}")
    print(f"\U0001F534 Total Sent: {sent:.2f}")
    print(f"\u2705 Available Balance: {received - sent:.2f}")

def mine_block():
    """
    Mines a new block including all open transactions and adds mining reward.
    """
    if not open_transactions:
        print("\u26CF\ufe0f No open transactions. Mining only reward...")

    last_block = get_previous_block()
    hashed_block = get_hash(last_block)
    proof = proof_of_work()

    reward_transaction = {
        "sender": "MINING",
        "recipient": owner,
        "amount": MINING_REWARD,
    }

    # Include reward transaction in block transactions
    block_transactions = open_transactions[:] + [reward_transaction]

    block = {
        "previous_hash": hashed_block,
        "index": len(blockchain),
        "transactions": block_transactions,
        "proof": proof,
    }

    blockchain.append(block)
    open_transactions.clear()
    print("\u2705 Block mined successfully!")
    print(f"🔗 Block hash: {get_hash(block)}")
    get_balance_details(owner)

def get_transaction_amount():
    """
    Takes user input for a new transaction.
    """
    tx_sender = input("Who is sending? (default: Kdhungel): ") or owner
    tx_recipient = input("Who is the recipient? ")
    tx_amount = float(input("Enter transaction amount: "))
    return tx_sender, tx_recipient, tx_amount

def get_user_action():
    """
    Displays menu and returns user choice.
    """
    print("\nPlease choose an option:")
    print("1. Add a new transaction")
    print("2. Mine a block")
    print("3. View blockchain")
    print("4. Manipulate blockchain")
    print("5. View Participants")
    print("6. View Balance")
    print("7. Verify Transactions")
    print("8. Exit")
    return int(input("Enter your choice: "))

def verify_chain():
    """
    Validates blockchain integrity by comparing hashes and proofs.

    Returns:
        bool: True if chain is valid, False otherwise.
    """
    for i, block in enumerate(blockchain):
        if i == 0:
            continue
        previous_block = blockchain[i - 1]

        # Check previous hash pointer
        if block['previous_hash'] != get_hash(previous_block):
            print(f"\u26a0\ufe0f Blockchain tampered at block {i + 1}! Previous hash mismatch.")
            return False

        # Check PoW validity
        transactions = block['transactions']
        last_hash = block['previous_hash']
        proof = block['proof']

        if not valid_proof(transactions, last_hash, proof):
            print(f"\u26a0\ufe0f Invalid proof of work at block {i + 1}!")
            return False
    return True

def verify_transaction(tx):
    """
    Verifies if a transaction is valid based on sender's balance.
    """
    return get_balance(tx['sender']) >= tx['amount']

def verify_transactions():
    """
    Validates all open transactions.
    """
    return all(verify_transaction(tx) for tx in open_transactions)

def display_blockchain():
    """
    Pretty prints the full blockchain.
    """
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1} (Hash: {get_hash(block)}):")
        print(json.dumps(block, indent=4))
    print('-' * 40)

# Main Program Loop
waiting_for_input = True

while waiting_for_input:
    choice = get_user_action()

    match choice:
        case 1:
            tx_sender, recipient, amount = get_transaction_amount()
            if add_transaction(recipient, sender=tx_sender, amount=amount):
                print(open_transactions)
                if not verify_transactions():
                    print("\u274c Invalid transactions detected. Fix them before mining.")
                    open_transactions.pop()  # Remove invalid transaction
                else:
                    print("\u2705 Transaction added successfully! You can mine a block (option 2) to confirm.")
        case 2:
            mine_block()
        case 3:
            display_blockchain()
        case 4:
            if len(blockchain) >= 2:
                blockchain[1]['transactions'] = [{"sender": "Hacker", "recipient": "Evil", "amount": 9999}]
                print("\u26a0\ufe0f Blockchain manipulated at block 2!")
            else:
                print("Not enough blocks to manipulate.")
        case 5:
            print("Participants in network:")
            print(participants)
        case 6:
            participant = input("Enter participant name: ")
            get_balance_details(participant)
        case 7:
            if verify_transactions():
                print("\u2705 All open transactions are valid.")
            else:
                print("\u274c Some open transactions are invalid!")
        case 8:
            display_blockchain()
            print("Exiting...")
            waiting_for_input = False
        case _:
            print("Invalid choice. Please try again.")

    if not verify_chain():
        display_blockchain()
        print("\u274c Blockchain integrity compromised! Exiting...")
        break
else:
    print("User Left")

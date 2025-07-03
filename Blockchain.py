import json
from functools import reduce
import os
from hash_util import hash_string_256, get_hash


# Constants
MINING_REWARD = 10  # Reward given to miner for mining a block

# The first block in the blockchain (Genesis block)
genesis_block = {
    "previous_hash": '0',  # No previous block
    "index": 0,            # Position in the chain
    "transactions": [],    # No transactions in genesis block
    "proof": 100           # Arbitrary proof number for genesis block
}

# Initialize blockchain with the genesis block as the first block
blockchain = [genesis_block]

# Store unconfirmed transactions which are yet to be mined into a block
open_transactions = []

# Owner (default sender and miner in this simple blockchain)
owner = "Kdhungel"

# Set of all participants who have been involved in any transaction
participants = {owner}


def save_data():
    """
    Save blockchain data, open transactions, and participants
    to a JSON file for persistence between program runs.
    """
    data = {
        "chain": blockchain,
        "open_transactions": open_transactions,
        "participants": list(participants)
    }

    # Ensure the 'data' directory exists before saving
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/blockchain.json", "w") as file:
            json.dump(data, file, indent=4)  # Pretty-print JSON with indentation
    except IOError as e:
        print(f"⚠️ Error saving data: {e}")


def load_data():
    """
    Load blockchain data, open transactions, and participants
    from JSON file. If file doesn't exist, is empty, or is corrupted,
    start fresh with genesis block.
    """
    global blockchain, open_transactions, participants
    try:
        with open("data/blockchain.json", "r") as file:
            content = file.read().strip()
            if not content:
                print("📁 Blockchain data file is empty. Starting fresh.")
                blockchain[:] = [genesis_block]
                open_transactions.clear()
                participants.clear()
                participants.add(owner)
                return
            data = json.loads(content)
            blockchain[:] = data.get("chain", [genesis_block])
            open_transactions[:] = data.get("open_transactions", [])
            participants.clear()
            participants.update(data.get("participants", [owner]))
    except (IOError, json.JSONDecodeError):
        print("📁 No valid saved data found. Starting fresh.")
        blockchain[:] = [genesis_block]
        open_transactions.clear()
        participants.clear()
        participants.add(owner)


def get_previous_block():
    """
    Returns the last block in the blockchain.
    """
    return blockchain[-1] if blockchain else None


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    Adds a new transaction to open transactions list after
    validating sender’s balance.

    Args:
        recipient (str): Recipient's identifier
        sender (str): Sender's identifier, defaults to owner
        amount (float): Amount to transfer

    Returns:
        bool: True if transaction is valid and added, False otherwise
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
    participants.update([recipient, sender])  # Add participants to set
    save_data()  # Save state after transaction added
    return True


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
    guess = (json.dumps(transactions, sort_keys=True) + last_hash + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    # Uncomment to debug proof attempts:
    # print(f"Guess: {guess_hash}")
    return guess_hash[:4] == "0000"


def proof_of_work():
    """
    Simple Proof of Work algorithm:
    - Finds a number 'proof' such that hash of
      (open transactions + last block hash + proof)
      starts with '0000'.

    Returns:
        int: Valid proof number
    """
    last_block = blockchain[-1]
    last_hash = get_hash(last_block)

    # Include mining reward transaction in proof calculation
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
    Calculates total amounts sent and received by participant
    by iterating through all blocks and their transactions.

    Args:
        participant (str): Participant identifier

    Returns:
        tuple: (total_sent, total_received)
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
    Calculates and returns the net balance of a participant.

    Args:
        participant (str): Participant identifier

    Returns:
        float: Available balance (received - sent)
    """
    sent, received = calculate_balance_details(participant)
    return received - sent


def get_balance_details(participant):
    """
    Prints detailed balance information for a participant,
    including total received, total sent, and net balance.

    Args:
        participant (str): Participant identifier
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
    Mines a new block by:
    - Performing proof of work
    - Creating a reward transaction for the miner
    - Adding open transactions + reward into a new block
    - Adding the block to the blockchain
    - Clearing open transactions
    - Saving updated blockchain state
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

    # Include reward transaction with open transactions in new block
    block_transactions = open_transactions[:] + [reward_transaction]

    block = {
        "previous_hash": hashed_block,
        "index": len(blockchain),
        "transactions": block_transactions,
        "proof": proof,
    }

    blockchain.append(block)  # Add new block to chain
    open_transactions.clear()  # Reset open transactions

    print("\u2705 Block mined successfully!")
    print(f"🔗 Block hash: {get_hash(block)}")
    get_balance_details(owner)  # Show miner balance
    save_data()


def get_transaction_amount():
    """
    Helper function to get user input for a new transaction.
    Added exception handling for invalid input.

    Returns:
        tuple: (sender, recipient, amount)
    """
    tx_sender = input("Who is sending? (default: Kdhungel): ") or owner
    tx_recipient = input("Who is the recipient? ")
    while True:
        try:
            tx_amount = float(input("Enter transaction amount: "))
            break
        except ValueError:
            print("⚠️ Invalid amount. Please enter a valid number.")
    return tx_sender, tx_recipient, tx_amount


def get_user_action():
    """
    Displays the main menu and returns user's choice.
    Added exception handling for invalid input.

    Returns:
        int: User's selected option number
    """
    while True:
        print("\nPlease choose an option:")
        print("1. Add a new transaction")
        print("2. Mine a block")
        print("3. View blockchain")
        print("4. Manipulate blockchain")
        print("5. View Participants")
        print("6. View Balance")
        print("7. Verify Transactions")
        print("8. Exit")
        try:
            choice = int(input("Enter your choice: "))
            return choice
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")


def verify_chain():
    """
    Validates the integrity of the blockchain by checking:
    - That each block's previous_hash matches the actual hash of the previous block
    - That each block's proof of work is valid

    Returns:
        bool: True if blockchain is valid, False otherwise
    """
    for i, block in enumerate(blockchain):
        if i == 0:
            continue  # Skip genesis block

        previous_block = blockchain[i - 1]

        # Check previous hash pointer matches
        if block['previous_hash'] != get_hash(previous_block):
            print(f"\u26a0\ufe0f Blockchain tampered at block {i + 1}! Previous hash mismatch.")
            return False

        # Validate proof of work
        transactions = block['transactions']
        last_hash = block['previous_hash']
        proof = block['proof']

        if not valid_proof(transactions, last_hash, proof):
            print(f"\u26a0\ufe0f Invalid proof of work at block {i + 1}!")
            return False

    return True


def verify_transaction(tx):
    """
    Checks if a transaction is valid by confirming
    the sender has enough balance.

    Args:
        tx (dict): Transaction dictionary

    Returns:
        bool: True if valid, False otherwise
    """
    return get_balance(tx['sender']) >= tx['amount']


def verify_transactions():
    """
    Validates all open (pending) transactions.

    Returns:
        bool: True if all transactions are valid, False otherwise
    """
    return all(verify_transaction(tx) for tx in open_transactions)


def display_blockchain():
    """
    Pretty prints the entire blockchain to the console.
    """
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1} (Hash: {get_hash(block)}):")
        print(json.dumps(block, indent=4))
    print('-' * 40)


# Main Program Loop
load_data()  # Load blockchain and open transactions from disk
waiting_for_input = True

try:
    while waiting_for_input:
        choice = get_user_action()

        match choice:
            case 1:
                # Add a new transaction
                tx_sender, recipient, amount = get_transaction_amount()
                if add_transaction(recipient, sender=tx_sender, amount=amount):
                    print(open_transactions)
                    # Check if all open transactions remain valid after addition
                    if not verify_transactions():
                        print("\u274c Invalid transactions detected. Fix them before mining.")
                        open_transactions.pop()  # Remove invalid transaction
                    else:
                        print("\u2705 Transaction added successfully! You can mine a block (option 2) to confirm.")
            case 2:
                # Mine a block to confirm transactions
                mine_block()
            case 3:
                # Display entire blockchain
                display_blockchain()
            case 4:
                # Demonstrate blockchain tampering by modifying transactions in block 2
                if len(blockchain) >= 2:
                    blockchain[1]['transactions'] = [{"sender": "Hacker", "recipient": "Evil", "amount": 9999}]
                    print("\u26a0\ufe0f Blockchain manipulated at block 2!")
                else:
                    print("Not enough blocks to manipulate.")
                save_data()
            case 5:
                # Display all participants in network
                print("Participants in network:")
                print(participants)
            case 6:
                # Show detailed balance of a participant
                participant = input("Enter participant name: ")
                get_balance_details(participant)
            case 7:
                # Verify all open transactions
                if verify_transactions():
                    print("\u2705 All open transactions are valid.")
                else:
                    print("\u274c Some open transactions are invalid!")
            case 8:
                # Exit program after displaying blockchain
                display_blockchain()
                print("Exiting...")
                waiting_for_input = False
            case _:
                print("Invalid choice. Please try again.")

        # Check blockchain integrity after every operation
        if not verify_chain():
            display_blockchain()
            print("\u274c Blockchain integrity compromised! Exiting...")
            break
except Exception as e:
    print(f"⚠️ Unexpected error occurred: {e}")

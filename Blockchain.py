import json
from functools import reduce
import os
from hash_util import hash_string_256, get_hash
from block import Block
from transaction import Transaction
from verification import Verification
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
verifier = Verification()

# Constants
MINING_REWARD = 10  # Reward given to miner for mining a block

# The first block in the blockchain (Genesis block)
genesis_block = Block(0, '0', [], 100)


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
        "chain": [block.to_dict() for block in blockchain],
        "open_transactions": [tx.to_dict() for tx in open_transactions],
        "participants": list(participants)
    }

    # Ensure the 'data' directory exists before saving
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/blockchain.json", "w") as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        logging.error(f"⚠️ Error saving data: {e}")

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

            #Convert blocks to Block Object
            blockchain[:] = [Block.from_dict(b) for b in data.get("chain", [])]

            open_transactions[:] = [Transaction.from_dict(tx) for tx in data.get("open_transactions", [])]
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
    Validates sender's balance before adding the transaction.

    Args:
        recipient (str): Recipient's identifier
        sender (str): Sender's identifier, defaults to owner
        amount (float): Amount to transfer

    Returns:
        bool: True if transaction is valid and added, False otherwise
    """
    # Reject zero or negative amounts
    if amount <= 0:
        logging.error("Transaction failed: Amount must be greater than zero.")
        return False

    sender_balance = get_balance(sender)
    if sender_balance < amount:
        logging.error("Transaction failed: %s has only %.2f available.", sender, sender_balance)
        return False

    transaction = Transaction(sender, recipient, amount)
    open_transactions.append(transaction)
    participants.update([recipient, sender])  # Add participants to set
    save_data()  # Save state after transaction added
    logging.info("Transaction added successfully: %s -> %s: %.2f", sender, recipient, amount)
    return True




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
    last_hash = get_hash(last_block.to_dict())

    # Include mining reward transaction in proof calculation
    transactions = open_transactions[:] + [Transaction("MINING", owner, MINING_REWARD)]

    proof = 0

    while not verifier.valid_proof(transactions, last_hash, proof):
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
        return total + reduce(lambda acc, tx: acc + tx.amount if tx.sender == participant else acc,
                              block.transactions, 0)

    def reduce_received(total, block):
        return total + reduce(lambda acc, tx: acc + tx.amount if tx.recipient == participant else acc,
                              block.transactions, 0)

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
        return False  # Indicate failure

    sent, received = calculate_balance_details(participant)
    print(f"\n\U0001F4CA Balance Report for {participant}")
    print(f"\U0001F7E2 Total Received: {received:.2f}")
    print(f"\U0001F534 Total Sent: {sent:.2f}")
    print(f"\u2705 Available Balance: {received - sent:.2f}")
    return True  # Indicate success


def mine_block():
    """
    Mines a new block by:
    - Performing proof of work
    - Creating a reward transaction for the miner
    - Adding open transactions + reward into a new block
    - Adding the block to the blockchain
    - Clearing open transactions
    - Saving updated blockchain state
    Mining reward is added as a transaction with "MINING" as sender.
    """
    if not open_transactions:
        print("\u26CF\ufe0f No open transactions. Mining only reward...")

    last_block = get_previous_block()
    hashed_block = get_hash(last_block.to_dict())
    proof = proof_of_work()

    reward_transaction = Transaction("MINING", owner, MINING_REWARD)

    # Include reward transaction with open transactions in new block
    block_transactions = open_transactions[:] + [reward_transaction]

    block = Block(len(blockchain), hashed_block, block_transactions, proof)

    blockchain.append(block)  # Add new block to chain
    open_transactions.clear()  # Reset open transactions

    print("\u2705 Block mined successfully!")
    print(f"🔗 Block hash: {get_hash(block.to_dict())}")
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
            logging.error("⚠️ Invalid amount. Please enter a valid number.")
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
        print("8. Verify Entire Blockchain")
        print("9. Exit")
        try:
            choice = int(input("Enter your choice: "))
            return choice
        except ValueError:
            print("⚠️ Invalid input. Please enter a number.")

def display_blockchain():
    """
    Pretty prints the entire blockchain to the console.
    """
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1} (Hash: {get_hash(block.to_dict())}):")
        print(block)  # __repr__ output, concise summary
        print(json.dumps(block.to_dict(), indent=4))  # full details
        print()

    print('-' * 40)

def handle_add_transaction():
    """
       Handle the process of adding a new transaction.

       - Takes input for sender, recipient, and amount.
       - Validates the transaction.
       - Adds it to the open transactions pool if valid.
       """
    # Add a new transaction
    tx_sender, recipient, amount = get_transaction_amount()
    if add_transaction(recipient, sender=tx_sender, amount=amount):
        print(open_transactions)
        # Check if all open transactions remain valid after addition
        if not verifier.verify_transactions(lambda tx: verifier.verify_transaction(tx, get_balance), open_transactions):
            logging.error("\u274c Invalid transactions detected. Fix them before mining.")
            open_transactions.pop()  # Remove invalid transaction
        else:
            print("\u2705 Transaction added successfully! You can mine a block (option 2) to confirm.")

def handle_mine_block():
    """
    Handle the mining process for the next block.

    - Performs proof of work.
    - Adds reward transaction.
    - Confirms all open transactions into a block.
    """
    mine_block()


def handle_display_blockchain():
    """
    Display all blocks currently in the blockchain.

    Each block is shown with its hash and contents.
    """
    display_blockchain()

def handle_tamper_blockchain():
    """
    Intentionally tamper with block 2 to simulate a blockchain attack.

    - Replaces transactions in the second block.
    - Saves the corrupted state.
    """
    if len(blockchain) >= 2:
        blockchain[1].transactions = [Transaction("Hacker", "Evil", 9999)]
        logging.error("⚠️ Blockchain manipulated at block 2!")
    else:
        logging.error("Not enough blocks to manipulate.")
    save_data()

def handle_show_participants():
    """
    Display all known participants in the blockchain network.

    Participants are collected from all transactions.
    """
    print("Participants in network:")
    print(participants)

def handle_check_balance():
    """
    Prompt user for a participant and show their balance details.

    - If the participant does not exist, show an error.
    - Otherwise, print sent, received, and available balance.
    """
    participant = input("Enter participant name: ")
    if not get_balance_details(participant):
        logging.error("Please check the participant name and try again.")

def handle_verify_transactions():
    """
    Verify all open (unconfirmed) transactions.

    - Ensures all transactions are valid.
    - Warns if any transaction would fail upon mining.
    """
    if verifier.verify_transactions():
        print("✅ All open transactions are valid.")
    else:
        logging.error("❌ Some open transactions are invalid!")

def handle_exit_program():
    """
    Exit the program gracefully.

    - Displays the final blockchain.
    - Saves the current state to disk.
    """
    display_blockchain()
    print("Exiting...")
    save_data()

def handle_verify_chain():
    """
    Verifies the integrity of the entire blockchain.

    - Checks that each block’s `previous_hash` matches the actual hash of the previous block.
    - Validates the proof of work for each block.
    - Skips the genesis block as it has no predecessor.
    - Prints result to console indicating whether the blockchain is valid or has been tampered with.
    """
    if verifier.verify_chain(blockchain):
        print("✅ Blockchain integrity OK.")
    else:
        logging.error("❌ Blockchain integrity has been compromised!")




# Main Program Loop
load_data()  # Load blockchain and open transactions from disk
waiting_for_input = True

try:
    while waiting_for_input:
        choice = get_user_action()

        match choice:
            case 1:
                handle_add_transaction()
            case 2:
                handle_mine_block()
            case 3:
                handle_display_blockchain()
            case 4:
                handle_tamper_blockchain()
            case 5:
                handle_show_participants()
            case 6:
                handle_check_balance()
            case 7:
                handle_verify_transactions()
            case 8:
                handle_verify_chain()
            case 9:
                handle_exit_program()
                waiting_for_input = False
            case _:
                logging.error("Invalid choice. Please try again.")

        # Check blockchain integrity after every operation
        if not verifier.verify_chain(blockchain):
            display_blockchain()
            logging.error("\u274c Blockchain integrity compromised! Exiting...")
            break
except Exception as e:
    logging.error(f"⚠️ Unexpected error occurred: {e}")

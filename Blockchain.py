import json
MINING_REWARD = 10

genesis_block = {
    "previous_hash": '0',
    "index": 0,
    "transactions": [],
}

# Initialize an empty blockchain list to store blocks
blockchain = []
blockchain = [genesis_block]

open_transactions = []
owner = "Kdhungel"
participants = {"Kdhungel"}


def get_previous_block():
    """
    Returns the last block in the blockchain, or None if the blockchain is empty.

    Returns:
        list or None: The last block in the blockchain or None if empty.
    """
    if len(blockchain) == 0:
        return None
    return blockchain[-1]  # Return the last block

def add_transaction(recipient, sender = owner, amount = 1.0):
    """
    Adds a new block to the blockchain.

    Args:
        :sender: The sender address.
        :recipient: The recipient address.
        :amount: Amount to add.
    """
    sender_balance = get_balance(sender)
    if sender_balance < amount:
        print(f"❌ Transaction failed: {sender} has only {sender_balance:.2f} available.")
        return False

    transaction = {
       "sender": sender,
       "recipient": recipient,
       "amount": amount,
   }
    open_transactions.append(transaction)
    participants.add(recipient)
    participants.add(sender)


    # Add a new block which stores the previous block and the current amount
def get_hash(block):
    return '-'.join([str(block[key]) for key in block])

def calculate_balance_details(participant):
    sent = sum(tx['amount'] for block in blockchain for tx in block['transactions'] if tx['sender'] == participant)
    received = sum(tx['amount'] for block in blockchain for tx in block['transactions'] if tx['recipient'] == participant)
    return sent, received

def get_balance(participant):
    sent, received = calculate_balance_details(participant)
    return received - sent

def get_balance_details(participant):
    sent, received = calculate_balance_details(participant)
    print(f"\n📊 Balance Report for {participant}")
    print(f"🟢 Total Received: {received:.2f}")
    print(f"🔴 Total Sent: {sent:.2f}")
    print(f"✅ Available Balance: {received - sent:.2f}")

def mine_block():
    if not open_transactions:
        print("⛏️ No open transactions. Mining only reward...")

    last_block = get_previous_block()
    hashed_block = get_hash(last_block)
    reward_transaction = {
        "sender": "MINING",
        "recipient": owner,
        "amount": MINING_REWARD,
    }

    block = {
        "previous_hash": hashed_block,
        "index": len(blockchain),
        "transactions": open_transactions[:] + [reward_transaction] ,
    }
    blockchain.append(block)
    open_transactions.clear()
    print("✅ Block mined successfully!")
    get_balance_details(owner)


def get_transaction_amount():
    """
    Prompts the user to enter a transaction amount.

    Returns:
        float: The transaction amount entered by the user.
    """
    tx_sender = input("Who is sending? (default: Kdhungel): ") or owner
    tx_recipient = input("Who is the recipient? ")
    tx_amount = float(input("Enter transaction amount: "))
    return tx_sender, tx_recipient, tx_amount


def get_user_action():
    """
    Prompts the user to select an action from the menu.

    Returns:
        int: The user's selected action.
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
    Verifies the integrity of the blockchain by ensuring each block points
    correctly to the previous block.

    Returns:
        bool: True if blockchain is valid, False otherwise.
    """

    for i, block in enumerate(blockchain):  # start from 1
        # Check if the previous block referenced in current block matches actual previous block
        if i == 0:
            continue

        if block['previous_hash'] != get_hash(blockchain[i - 1]):
            print(f"⚠️ Blockchain tampered at block {i + 1}!")
            return False
    return True

def verify_transaction(tx):
    sender_balance = get_balance(tx['sender'])
    return sender_balance >= tx['amount']

def verify_transactions():
    return all(verify_transaction(tx) for tx in open_transactions)


def display_blockchain():
    """
    Prints all blocks in the blockchain showing the previous block and the amount.
    """
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1}:")
        print(json.dumps(block, indent=4))
    print('-' * 20)

waiting_for_input = True
# Main program loop - runs until user exits or blockchain integrity is compromised
while waiting_for_input:
    choice = get_user_action()

    match choice:
        case 1:
            # Add a new transaction block with user input amount
            tx_sender, recipient, amount = get_transaction_amount()

            if add_transaction(recipient, sender=tx_sender, amount=amount):
                print(open_transactions)
                if not verify_transactions():
                    print("❌ Invalid transactions detected. Fix them before mining.")
                    continue
                mine_block()
                get_balance_details(owner)

        case 2:
            mine_block()

        case 3:
            # Display all blocks in the blockchain
            display_blockchain()
        case 4:
            if len(blockchain) >= 2:
                blockchain[1]['transactions'] = [{"sender": "Hacker", "recipient": "Evil", "amount": 9999}]
        case 5:
            print(participants)
        case 6:
            participant = input("Enter participant name: ")
            get_balance_details(participant)

        case 7:
            if verify_transactions():
                print("✅ All open transactions are valid.")
            else:
                print("❌ Some open transactions are invalid!")

        case 8:
            # Exit the program
            display_blockchain()
            print("Exiting...")
            waiting_for_input = False
        case _:
            display_blockchain()
            # Invalid choice input from user
            print("Invalid choice. Please try again.")
            # Verify blockchain after adding a new block
    if not verify_chain():
        display_blockchain()
        print("Blockchain integrity compromised! Exiting...")
        break

else:
    print("User Left")

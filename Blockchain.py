import json

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


def get_previous_block():
    """
    Returns the last block in the blockchain, or None if the blockchain is empty.

    Returns:
        list or None: The last block in the blockchain or None if empty.
    """
    if len(blockchain) == 0:
        return None
    return blockchain[-1]  # Return the last block

def add_block(recipient, sender = owner, amount = 1.0):
    """
    Adds a new block to the blockchain.

    Args:
        :sender: The sender address.
        :recipient: The recipient address.
        :amount: Amount to add.
    """
    transaction = {
       "sender": sender,
       "recipient": recipient,
       "amount": amount,
   }
    open_transactions.append(transaction)

    # Add a new block which stores the previous block and the current amount
def get_hash(block):
    return '-'.join([str(block[key]) for key in block])


def mine_block():
    last_block = get_previous_block()
    hashed_block = get_hash(last_block)

    block = {
        "previous_hash": hashed_block,
        "index": len(blockchain),
        "transactions": open_transactions,
    }
    blockchain.append(block)
    open_transactions.clear()


def get_transaction_amount():
    """
    Prompts the user to enter a transaction amount.

    Returns:
        float: The transaction amount entered by the user.
    """
    tx_recipient = input("Who is your transaction recipient? ")
    tx_amount =  float(input("Enter transaction amount: "))
    return tx_amount, tx_recipient


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
    print("5. Exit")
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
            tx_data = get_transaction_amount()
            amount , recipient = tx_data
            add_block(recipient, amount=amount)
            print(open_transactions)
            mine_block()

        case 2:
            mine_block()

        case 3:
            # Display all blocks in the blockchain
            display_blockchain()
        case 4:
            if len(blockchain) >= 1:
                blockchain[0] = {
                    "previous_hash": get_hash(blockchain[0]),
                    "index": len(blockchain),
                    "transactions": open_transactions,
                }
        case 5:
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




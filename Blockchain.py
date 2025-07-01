# Initialize an empty blockchain list to store blocks
blockchain = []

def get_previous_block():
    """
    Returns the last block in the blockchain, or None if the blockchain is empty.

    Returns:
        list or None: The last block in the blockchain or None if empty.
    """
    if len(blockchain) == 0:
        return None
    return blockchain[-1]  # Return the last block

def add_block(amount, previous_block):
    """
    Adds a new block to the blockchain.

    Args:
        amount (float): The transaction amount to store in this block.
        previous_block (list or None): The previous block in the chain,
            or None if this is the first block (genesis block).
    """
    # If this is the first block (genesis), create a dummy previous block
    if previous_block is None:
        previous_block = [1]  # Genesis block

    # Add a new block which stores the previous block and the current amount
    blockchain.append([previous_block, amount])

def get_transaction_amount():
    """
    Prompts the user to enter a transaction amount.

    Returns:
        float: The transaction amount entered by the user.
    """
    return float(input("Enter transaction amount: "))

def get_user_action():
    """
    Prompts the user to select an action from the menu.

    Returns:
        int: The user's selected action.
    """
    print("\nPlease choose an option:")
    print("1. Add a new transaction")
    print("2. View blockchain")
    print("3. Exit")
    return int(input("Enter your choice: "))

def verify_chain():
    """
    Verifies the integrity of the blockchain by ensuring each block points
    correctly to the previous block.

    Returns:
        bool: True if blockchain is valid, False otherwise.
    """
    for block_index in range(1, len(blockchain)):  # start from 1
        # Check if the previous block referenced in current block matches actual previous block
        if blockchain[block_index][0] != blockchain[block_index - 1]:
            print(f"⚠️ Blockchain tampered at block {block_index + 1}!")
            return False
    return True

def display_blockchain():
    """
    Prints all blocks in the blockchain showing the previous block and the amount.
    """
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1}: {block[0]} -> {block[1]}")
    else:
        print('-' * 20)

waiting_for_input = True
# Main program loop - runs until user exits or blockchain integrity is compromised
while waiting_for_input:
    choice = get_user_action()

    match choice:
        case 1:
            # Add a new transaction block with user input amount
            amount = get_transaction_amount()
            add_block(amount, get_previous_block())
            # Verify blockchain after adding a new block
            if not verify_chain():
                print("Blockchain integrity compromised! Exiting...")
                break
        case 2:
            # Display all blocks in the blockchain
            display_blockchain()
        case 3:
            # Exit the program
            display_blockchain()
            print("Exiting...")
            waiting_for_input = False
        case _:
            display_blockchain()
            # Invalid choice input from user
            print("Invalid choice. Please try again.")
else:
    print("User Left")
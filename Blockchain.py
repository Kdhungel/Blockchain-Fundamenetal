# Initialize an empty blockchain list to store blocks
blockchain = []

def get_previous_block():
    """Returns the last block in the blockchain, or None if the blockchain is empty."""
    if len(blockchain) == 0:
        return None
    return blockchain[-1]  # Return the last block

def add_block(amount, previous_block):
    """Adds a new block to the blockchain.

    Args:
        amount (float): The transaction amount to store in this block.
        previous_block (list or None): The previous block in the chain, or None if this is the first block.
    """
    # If this is the first block (genesis), create a dummy previous block
    if previous_block is None:
        previous_block = [1]  # Genesis block

    # Add a new block which stores the previous block and the current amount
    blockchain.append([previous_block, amount])

def get_transaction_amount():
    """Prompts the user to enter a transaction amount and returns it as a float."""
    return float(input("Enter transaction amount: "))

def get_user_action():
    """Prompts the user to select an option and returns the selected choice as an integer."""
    print("\nPlease choose an option:")
    print("1. Add a new transaction")
    print("2. View blockchain")
    print("3. Exit")
    return int(input("Enter your choice: "))

def verify_chain():
    """Checks if the blockchain is valid by making sure each block points to the correct previous block."""
    block_index = 0
    is_valid = True

    # Loop through each block in the blockchain
    for block in blockchain:
        # Skip the first block since it has no previous block to verify
        if block_index == 0:
            block_index += 1
            continue

        # Check if the previous block stored in the current block matches the actual previous block in the list
        elif block[0] == blockchain[block_index - 1]:
            is_valid = True  # This block is valid, continue checking
        else:
            is_valid = False  # Blockchain is broken, previous block does not match
            break

        block_index += 1  # Move to next block index

    return is_valid

def display_blockchain():
    """Prints all blocks in the blockchain showing the previous block and the amount."""
    for i, block in enumerate(blockchain):
        print(f"Block {i + 1}: {block[0]} -> {block[1]}")

# Main program loop - runs until user exits or blockchain is invalid
while True:
    choice = get_user_action()

    match choice:
        case 1:
            # Add a new transaction block with user input amount
            amount = get_transaction_amount()
            add_block(amount, get_previous_block())
        case 2:
            # Display all blocks in the blockchain
            display_blockchain()
        case 3:
            # Exit the program
            print("Exiting...")
            break
        case _:
            # Invalid choice input from user
            print("Invalid choice. Please try again.")

    # Verify if blockchain is valid after each operation
    if not verify_chain():
        print("Invalid transaction amount. Please try again.")
        break

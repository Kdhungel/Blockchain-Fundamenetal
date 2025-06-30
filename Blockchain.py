# Initializing the block chain
blockchain = []

def get_last_block_value():
    """ Returns the last value in the blockchain """
    return  blockchain[-1]

def add_value(transaction_amount, last_transaction = [1]):
    """ Adds a new transaction to the blockchain
    Parameters:
        transaction_amount (int): The amount of the transaction
        last_transaction (list): The last value in the blockchain
    """
    blockchain.append([last_transaction, transaction_amount])

def get_user_input():
    return float(input("Enter the amount for transaction: "))

tx_amount = get_user_input()

add_value(tx_amount)

while (True):
    tx_amount = get_user_input()
    add_value(tx_amount, get_last_block_value())

    for block in blockchain:
        print(f"Blocks: {block[0]} -> {block[1]}")

print("Done")

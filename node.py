import logging
from verification import Verification
from hash_util import get_hash

from transaction import Transaction
import json

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class Node:
    """
    Node class handles user interaction for the blockchain system.
    Provides functionality to perform transactions, mine blocks,
    view and tamper the blockchain, and verify integrity.
    """
    def __init__(self, blockchain):
        """
        Initialize the Node with a Blockchain instance.

        Args:
            blockchain (Blockchain): The Blockchain instance.
        """
        self.blockchain = blockchain
        self.verifier = blockchain.verifier

    def listen_for_inputs(self):
        """
        Main loop that listens for user input and performs appropriate actions.
        """
        self.blockchain.load_data()
        waiting_for_input = True

        try:
            while waiting_for_input:
                choice = self.get_user_action()

                match choice:
                    case 1:
                        self.handle_add_transaction()
                    case 2:
                        self.handle_mine_block()
                    case 3:
                        self.handle_display_blockchain()
                    case 4:
                        self.handle_tamper_blockchain()
                    case 5:
                        self.handle_show_participants()
                    case 6:
                        self.handle_check_balance()
                    case 7:
                        self.handle_verify_transactions()
                    case 8:
                        self.handle_verify_chain()
                    case 9:
                        self.handle_exit_program()
                        waiting_for_input = False
                    case _:
                        logging.error("Invalid choice. Please try again.")

                if not self.verifier.verify_chain(self.blockchain.blockchain):
                    self.display_blockchain()
                    logging.error("\u274c Blockchain integrity compromised! Exiting...")
                    break
        except Exception as e:
            logging.error(f"⚠️ Unexpected error occurred: {e}")

    def get_user_action(self):
        """
        Display the menu and get the user's action.

        Returns:
            int: User's choice from the menu.
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
                return int(input("Enter your choice: "))
            except ValueError:
                print("⚠️ Invalid input. Please enter a number.")

    def display_blockchain(self):
        """
        Display the blockchain with block hash and full contents.
        """
        for i, block in enumerate(self.blockchain.blockchain):
            label = "Genesis Block" if i == 0 else f"Block {i}"
            print(f"{label} (Hash: {get_hash(block.to_dict())}):")
            print(block)
            print(json.dumps(block.to_dict(), indent=4))
            print()
        print('-' * 40)

    def handle_add_transaction(self):
        """
        Handles input and validation for adding a new transaction.
        """
        sender, recipient, amount = self.get_transaction_amount()
        if self.blockchain.add_transaction(recipient, sender=sender, amount=amount):
            print(self.blockchain.open_transactions)
            if not self.verifier.verify_transactions(
                lambda tx: self.verifier.verify_transaction(tx, self.blockchain.get_balance),
                self.blockchain.open_transactions):
                logging.error("\u274c Invalid transactions detected. Fix them before mining.")
                self.blockchain.open_transactions.pop()
            else:
                print("\u2705 Transaction added successfully! You can mine a block (option 2) to confirm.")

    def handle_mine_block(self):
        """
        Handles block mining triggered by the user.
        """
        miner_name = input("Enter miner name (default: Kdhungel): ") or self.blockchain.owner
        self.blockchain.mine_block(miner=miner_name)

    def handle_display_blockchain(self):
        """
        Displays the blockchain to the console.
        """
        self.display_blockchain()

    def handle_tamper_blockchain(self):
        """
        Intentionally manipulates block 2 to simulate blockchain tampering.
        """
        if len(self.blockchain.blockchain) >= 2:
            self.blockchain.blockchain[1].transactions = [Transaction("Hacker", "Evil", 9999)]
            logging.error("⚠️ Blockchain manipulated at block 2!")
            self.rebuild_participants()
        else:
            logging.error("Not enough blocks to manipulate.")
        self.blockchain.save_data()

    def rebuild_participants(self):
        """
        Rebuilds the participant list from the blockchain and open transactions.
        """
        self.blockchain.participants.clear()
        for block in self.blockchain.blockchain:
            for tx in block.transactions:
                self.blockchain.participants.update([tx.sender, tx.recipient])
        for tx in self.blockchain.open_transactions:
            self.blockchain.participants.update([tx.sender, tx.recipient])

    def handle_show_participants(self):
        """
        Displays all known participants in the network.
        """
        print("Participants in network:")
        print(self.blockchain.participants)

    def handle_check_balance(self):
        """
        Asks user for a participant name and shows their balance.
        """
        participant = input("Enter participant name: ")
        if not self.blockchain.get_balance_details(participant):
            logging.error("Please check the participant name and try again.")

    def handle_verify_transactions(self):
        """
        Verifies all open (unconfirmed) transactions.
        """
        if self.verifier.verify_transactions(
            lambda tx: self.verifier.verify_transaction(tx, self.blockchain.get_balance),
            self.blockchain.open_transactions):
            print("✅ All open transactions are valid.")
        else:
            logging.error("❌ Some open transactions are invalid!")

    def handle_exit_program(self):
        """
        Displays blockchain and exits the program.
        """
        self.display_blockchain()
        print("Exiting...")
        self.blockchain.save_data()

    def handle_verify_chain(self):
        """
        Verifies the integrity of the entire blockchain.
        """
        if self.verifier.verify_chain(self.blockchain.blockchain):
            print("✅ Blockchain integrity OK.")
        else:
            logging.error("❌ Blockchain integrity has been compromised!")

    def get_transaction_amount(self):
        """
        Collects transaction details from the user.

        Returns:
            tuple: (sender, recipient, amount)
        """
        sender = input("Who is sending? (default: Kdhungel): ") or self.blockchain.owner
        recipient = input("Who is the recipient? ")
        while True:
            try:
                amount = float(input("Enter transaction amount: "))
                break
            except ValueError:
                logging.error("⚠️ Invalid amount. Please enter a valid number.")
        return sender, recipient, amount
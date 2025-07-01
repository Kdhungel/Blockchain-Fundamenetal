# Simple Blockchain in Python

## Overview

This project is a simple implementation of a blockchain using Python.  
It demonstrates the basic principles of blockchain technology including:

- Creating blocks that store transaction amounts and reference the previous block
- Verifying blockchain integrity by ensuring each block correctly links to its predecessor
- Adding new transactions interactively via user input
- Viewing the entire blockchain in a readable format

This is a great learning tool for understanding how blockchains work at a fundamental level.

## Features

- Genesis block creation for the first transaction
- Nested blocks linking each new transaction to the previous one
- Chain verification to detect tampering or invalid data
- Command-line interface for adding transactions, viewing the blockchain, and exiting

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    ```

2. Navigate into the project directory:

    ```bash
    cd your-repo-name
    ```

3. Run the Python script:

    ```bash
    python blockchain.py
    ```

4. Follow the on-screen prompts to:

    - Add new transactions
    - View the blockchain
    - Exit the program

## How It Works

The blockchain is implemented as a list of blocks. Each block contains:

- A reference to the entire previous block (nested list structure)
- The transaction amount for that block

When a new block is added, it references the previous block, forming a chain.  
The `verify_chain()` function checks that every block’s previous reference matches the actual previous block in the list — ensuring the chain has not been tampered with.

## Future Improvements

- Add cryptographic hashing for block contents for stronger security
- Include timestamps for each transaction
- Implement proof-of-work or consensus algorithms
- Add persistent storage to save and load the blockchain

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

Feel free to open issues or submit pull requests if you'd like to contribute!

---

© 2025 Kritish Dhungel or https://github.com/Kdhungel

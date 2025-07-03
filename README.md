# Simple Blockchain in Python with Proof of Work

## Overview

This project is a straightforward Python implementation of a blockchain that introduces core blockchain concepts such as:

- Adding and validating transactions between participants
- Mining blocks with a Proof of Work (PoW) consensus mechanism
- Rewarding miners with mining rewards
- Verifying blockchain integrity by validating hashes and PoW
- Tracking participant balances based on transaction history
- Interactive command-line interface to manage the blockchain

This project is designed as a learning tool to help understand the foundational principles of blockchains, cryptographic hashing, and consensus algorithms.

## Features

- Genesis block initialization with a preset proof
- Transaction validation ensuring senders have sufficient balance
- Mining blocks by finding a nonce that produces a hash with leading zeros (PoW)
- Automatic mining reward transactions added to mined blocks
- Complete chain verification that checks previous hashes and PoW validity
- Interactive CLI for adding transactions, mining, viewing blockchain, and participant balances
- Ability to simulate tampering to demonstrate chain verification failure

## Usage

1. Clone the repository:

    ```bash
    git clone https://github.com/Kdhungel/Blockchain-Fundamenetal.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Blockchain-Fundamenetal
    ```

3. Run the blockchain script:

    ```bash
    python blockchain.py
    ```

4. Follow the command line menu to:

    - Add new transactions  
    - Mine blocks to confirm transactions and earn rewards  
    - View the blockchain and participant balances  
    - Verify transaction and chain integrity  
    - Experiment with blockchain tampering  

## How It Works

- **Blocks and Chain:** The blockchain is a list of blocks, each containing transactions, a proof (nonce), and the hash of the previous block. This forms a cryptographically linked chain.

- **Proof of Work:** Mining a block involves finding a number (`proof`) such that the SHA-256 hash of the block’s transactions, the previous block’s hash, and the proof starts with four leading zeros (`0000`). This computational puzzle secures the network.

- **Transactions and Balances:** Participants can send amounts to others. Transactions are verified to ensure senders have enough balance before being added to open transactions.

- **Mining Reward:** Miners receive a fixed reward transaction automatically added to each mined block, incentivizing mining.

- **Verification:** The chain is validated by checking each block’s previous hash and proof of work. Tampering with transactions or block data breaks verification.

## Future Improvements

- Add timestamping for blocks and transactions  
- Implement networking to enable multiple nodes and distributed consensus  
- Add persistent storage to save/load blockchain state  
- Explore more advanced consensus mechanisms like Proof of Stake  
- Implement smart contract capabilities  

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

Feel free to open issues or submit pull requests to improve the project!

---

© 2025 Kritish Dhungel | [GitHub](https://github.com/Kdhungel)

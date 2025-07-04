from Blockchain import Blockchain
from node import Node

if __name__ == "__main__":
    blockchain = Blockchain("Kdhungel")
    node = Node(blockchain)
    node.listen_for_inputs()

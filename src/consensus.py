import hashlib
import time
import json

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        
    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = Block(
            index=len(self.chain) + 1,
            transactions=self.current_transactions,
            timestamp=time.time(),
            previous_hash=previous_hash or self.last_block.compute_hash(),
            nonce=proof
        )

        self.current_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block.index + 1

    def proof_of_work(self, block):
        difficulty = 4
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return block.nonce

    def is_valid(self):
        block = self.chain[0]
        if block.index != 1 or block.previous_hash != '1':
            return False

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.compute_hash():
                return False

            if not self.is_valid_proof(current_block):
                return False

        return True

    def is_valid_proof(self, block):
        difficulty = 4
        return block.compute_hash().startswith('0' * difficulty)

# Example usage
blockchain = Blockchain()

blockchain.new_transaction('Alice', 'Bob', 5.0)
blockchain.new_transaction('Bob', 'Charlie', 2.5)
blockchain.new_block(blockchain.proof_of_work(blockchain.last_block))

blockchain.new_transaction('Charlie', 'David', 1.0)
blockchain.new_transaction('David', 'Alice', 0.5)
blockchain.new_block(blockchain.proof_of_work(blockchain.last_block))

print(blockchain.chain)

import hashlib
import time

class ConsensusProtocol:
    def __init__(self, participants):
        self.participants = participants
        self.block_chain = []
        self.current_block = {'index': 0, 'timestamp': time.time(), 'data': 'Genesis Block', 'previous_hash': '0'}
        self.block_chain.append(self.current_block)

    def calculate_hash(self, block):
        block_string = str(block['index']) + str(block['timestamp']) + str(block['data']) + str(block['previous_hash'])
        return hashlib.sha256(block_string.encode()).hexdigest()

    def is_valid_block(self, block, previous_block):
        if block['index'] != previous_block['index'] + 1:
            return False
        if block['previous_hash'] != self.calculate_hash(previous_block):
            return False
        if self.calculate_hash(block) != block['hash']:
            return False
        return True

    def add_block(self, block):
        if self.is_valid_block(block, self.current_block):
            self.block_chain.append(block)
            self.current_block = block
            return True
        return False

    def reach_consensus(self):
        longest_chain = self.block_chain
        for participant in self.participants:
            participant_chain = participant.get_chain()
            if len(participant_chain) > len(longest_chain):
                longest_chain = participant_chain
        self.block_chain = longest_chain
        self.current_block = self.block_chain[-1]

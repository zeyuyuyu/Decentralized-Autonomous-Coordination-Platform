import hashlib
import time
import json

class ConsensusNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.voting_pool = []
        self.vote_tally = {}
        self.last_block_hash = None

    def add_vote(self, vote):
        self.voting_pool.append(vote)
        if vote['proposal'] in self.vote_tally:
            self.vote_tally[vote['proposal']] += 1
        else:
            self.vote_tally[vote['proposal']] = 1

    def get_consensus(self):
        max_votes = max(self.vote_tally.values())
        for proposal, votes in self.vote_tally.items():
            if votes == max_votes:
                return proposal
        return None

    def update_last_block_hash(self, block_hash):
        self.last_block_hash = block_hash

class DecentralizedVoting:
    def __init__(self, nodes):
        self.nodes = {node.node_id: node for node in nodes}

    def propose_vote(self, node_id, proposal):
        vote = {
            'node_id': node_id,
            'proposal': proposal,
            'timestamp': time.time(),
            'hash': hashlib.sha256(json.dumps(proposal).encode()).hexdigest()
        }
        for node in self.nodes.values():
            node.add_vote(vote)
        return vote

    def get_consensus(self):
        consensus = None
        for node in self.nodes.values():
            node_consensus = node.get_consensus()
            if node_consensus:
                if not consensus or self.nodes[consensus].vote_tally[node_consensus] < self.nodes[node_consensus].vote_tally[node_consensus]:
                    consensus = node_consensus
        return consensus

    def update_last_block_hash(self, block_hash):
        for node in self.nodes.values():
            node.update_last_block_hash(block_hash)

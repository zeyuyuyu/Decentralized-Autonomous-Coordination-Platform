import math
import random

class DPoSConsensus:
    def __init__(self, num_validators, stake_threshold):
        self.num_validators = num_validators
        self.stake_threshold = stake_threshold
        self.validators = []
        self.validator_stakes = {}
        self.validator_votes = {}

    def register_validator(self, validator_id, stake):
        if len(self.validators) < self.num_validators and stake >= self.stake_threshold:
            self.validators.append(validator_id)
            self.validator_stakes[validator_id] = stake
            self.validator_votes[validator_id] = 0

    def vote_for_block(self, validator_id, block_hash):
        if validator_id in self.validators:
            self.validator_votes[validator_id] += 1

    def select_block_producer(self):
        total_stake = sum(self.validator_stakes.values())
        probabilities = [stake / total_stake for stake in self.validator_stakes.values()]
        block_producer_index = random.choices(range(len(self.validators)), weights=probabilities, k=1)[0]
        return self.validators[block_producer_index]

    def finalize_block(self, block_hash):
        block_producer = self.select_block_producer()
        if self.validator_votes[block_producer] > math.floor(len(self.validators) / 2):
            return block_hash
        else:
            return None

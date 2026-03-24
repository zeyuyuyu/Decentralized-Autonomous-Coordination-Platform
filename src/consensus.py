# Byzantine Fault Tolerant Consensus Implementation using PBFT
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum
import hashlib
import time

class MessageType(Enum):
    PRE_PREPARE = 'pre-prepare'
    PREPARE = 'prepare' 
    COMMIT = 'commit'
    REPLY = 'reply'

@dataclass
class ConsensusMessage:
    msg_type: MessageType
    view_number: int
    sequence_number: int
    digest: str
    node_id: str
    timestamp: float
    signature: str = ''

class PBFTConsensus:
    def __init__(self, node_id: str, num_nodes: int, private_key: str):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.private_key = private_key
        self.view_number = 0
        self.sequence_number = 0
        self.prepared_messages: Dict[int, Set[ConsensusMessage]] = {}
        self.committed_messages: Dict[int, Set[ConsensusMessage]] = {}
        self.f = (num_nodes - 1) // 3  # Byzantine fault tolerance threshold

    def create_digest(self, message: str) -> str:
        return hashlib.sha256(message.encode()).hexdigest()

    def sign_message(self, message: ConsensusMessage) -> str:
        # Placeholder for actual signature implementation
        return f'{self.node_id}_{message.digest}'

    def verify_signature(self, message: ConsensusMessage) -> bool:
        # Placeholder for actual signature verification
        return message.signature.startswith(message.node_id)

    def broadcast_preprepare(self, client_request: str) -> ConsensusMessage:
        self.sequence_number += 1
        digest = self.create_digest(client_request)
        
        message = ConsensusMessage(
            msg_type=MessageType.PRE_PREPARE,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            digest=digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        message.signature = self.sign_message(message)
        return message

    def handle_preprepare(self, message: ConsensusMessage) -> ConsensusMessage:
        if not self.verify_signature(message):
            return None

        prepare_msg = ConsensusMessage(
            msg_type=MessageType.PREPARE,
            view_number=message.view_number,
            sequence_number=message.sequence_number,
            digest=message.digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        prepare_msg.signature = self.sign_message(prepare_msg)
        
        if message.sequence_number not in self.prepared_messages:
            self.prepared_messages[message.sequence_number] = set()
        self.prepared_messages[message.sequence_number].add(prepare_msg)
        
        return prepare_msg

    def handle_prepare(self, message: ConsensusMessage) -> ConsensusMessage:
        if not self.verify_signature(message):
            return None

        if message.sequence_number not in self.prepared_messages:
            self.prepared_messages[message.sequence_number] = set()
        self.prepared_messages[message.sequence_number].add(message)

        # Check if we have enough prepare messages
        if len(self.prepared_messages[message.sequence_number]) >= 2 * self.f:
            commit_msg = ConsensusMessage(
                msg_type=MessageType.COMMIT,
                view_number=message.view_number,
                sequence_number=message.sequence_number,
                digest=message.digest,
                node_id=self.node_id,
                timestamp=time.time()
            )
            commit_msg.signature = self.sign_message(commit_msg)
            return commit_msg
        return None

    def handle_commit(self, message: ConsensusMessage) -> bool:
        if not self.verify_signature(message):
            return False

        if message.sequence_number not in self.committed_messages:
            self.committed_messages[message.sequence_number] = set()
        self.committed_messages[message.sequence_number].add(message)

        # Check if we have enough commit messages
        if len(self.committed_messages[message.sequence_number]) >= 2 * self.f + 1:
            return True
        return False

    def check_consensus_reached(self, sequence_number: int) -> bool:
        return (sequence_number in self.committed_messages and
                len(self.committed_messages[sequence_number]) >= 2 * self.f + 1)

    def get_consensus_result(self, sequence_number: int) -> str:
        if self.check_consensus_reached(sequence_number):
            # Return the agreed-upon digest
            return next(iter(self.committed_messages[sequence_number])).digest
        return None

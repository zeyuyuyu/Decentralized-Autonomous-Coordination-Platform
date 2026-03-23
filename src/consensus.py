from typing import List, Dict, Set
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
    view_num: int
    seq_num: int
    digest: str
    node_id: str
    timestamp: float
    signature: str = ''

class PBFTConsensus:
    def __init__(self, node_id: str, total_nodes: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.view_number = 0
        self.sequence_number = 0
        self.prepared_msgs: Dict[str, Set[ConsensusMessage]] = {}
        self.committed_msgs: Dict[str, Set[ConsensusMessage]] = {}
        self.f = (total_nodes - 1) // 3  # Max Byzantine nodes tolerated

    def create_message(self, msg_type: MessageType, digest: str) -> ConsensusMessage:
        msg = ConsensusMessage(
            msg_type=msg_type,
            view_num=self.view_number,
            seq_num=self.sequence_number,
            digest=digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        msg.signature = self._sign_message(msg)
        return msg

    def handle_message(self, msg: ConsensusMessage) -> bool:
        if not self._verify_message(msg):
            return False

        if msg.msg_type == MessageType.PRE_PREPARE:
            return self._handle_pre_prepare(msg)
        elif msg.msg_type == MessageType.PREPARE:
            return self._handle_prepare(msg)
        elif msg.msg_type == MessageType.COMMIT:
            return self._handle_commit(msg)
        return False

    def _handle_pre_prepare(self, msg: ConsensusMessage) -> bool:
        if msg.view_num != self.view_number:
            return False

        if msg.digest not in self.prepared_msgs:
            self.prepared_msgs[msg.digest] = set()
        self.prepared_msgs[msg.digest].add(msg)

        prepare_msg = self.create_message(MessageType.PREPARE, msg.digest)
        return True

    def _handle_prepare(self, msg: ConsensusMessage) -> bool:
        if msg.digest not in self.prepared_msgs:
            return False

        self.prepared_msgs[msg.digest].add(msg)
        
        if len(self.prepared_msgs[msg.digest]) >= 2 * self.f + 1:
            commit_msg = self.create_message(MessageType.COMMIT, msg.digest)
            return True
        return False

    def _handle_commit(self, msg: ConsensusMessage) -> bool:
        if msg.digest not in self.committed_msgs:
            self.committed_msgs[msg.digest] = set()
        
        self.committed_msgs[msg.digest].add(msg)

        if len(self.committed_msgs[msg.digest]) >= 2 * self.f + 1:
            return self._finalize_consensus(msg.digest)
        return False

    def _finalize_consensus(self, digest: str) -> bool:
        self.sequence_number += 1
        return True

    def _sign_message(self, msg: ConsensusMessage) -> str:
        # TODO: Implement actual cryptographic signing
        content = f"{msg.msg_type}:{msg.view_num}:{msg.seq_num}:{msg.digest}:{msg.node_id}:{msg.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _verify_message(self, msg: ConsensusMessage) -> bool:
        # TODO: Implement actual signature verification
        expected_sig = self._sign_message(msg)
        return msg.signature == expected_sig

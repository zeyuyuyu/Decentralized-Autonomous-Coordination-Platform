from typing import Dict, List, Set
import hashlib
import time
from dataclasses import dataclass
from enum import Enum

class ConsensusState(Enum):
    PRE_PREPARE = 'pre_prepare'
    PREPARE = 'prepare' 
    COMMIT = 'commit'
    REPLY = 'reply'

@dataclass
class ConsensusMessage:
    msg_type: ConsensusState
    view_number: int
    sequence_number: int
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
        self.prepared_messages: Dict[int, Set[ConsensusMessage]] = {}
        self.committed_messages: Dict[int, Set[ConsensusMessage]] = {}
        self.current_state = ConsensusState.PRE_PREPARE
        
    def create_message(self, msg_type: ConsensusState, data: str) -> ConsensusMessage:
        """Create a new consensus message"""
        digest = hashlib.sha256(data.encode()).hexdigest()
        msg = ConsensusMessage(
            msg_type=msg_type,
            view_number=self.view_number,
            sequence_number=self.sequence_number,
            digest=digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        # TODO: Add real signature
        msg.signature = f'sig_{self.node_id}_{msg.sequence_number}'
        return msg

    def pre_prepare(self, data: str) -> ConsensusMessage:
        """Primary node initiates consensus with pre-prepare message"""
        if self.current_state != ConsensusState.PRE_PREPARE:
            raise Exception('Invalid state for pre-prepare')
            
        msg = self.create_message(ConsensusState.PRE_PREPARE, data)
        self.sequence_number += 1
        self.current_state = ConsensusState.PREPARE
        return msg

    def prepare(self, pre_prepare_msg: ConsensusMessage) -> ConsensusMessage:
        """Node validates pre-prepare and broadcasts prepare"""
        if self.current_state != ConsensusState.PREPARE:
            raise Exception('Invalid state for prepare')
            
        if pre_prepare_msg.view_number != self.view_number:
            raise Exception('Invalid view number')
            
        prepare_msg = ConsensusMessage(
            msg_type=ConsensusState.PREPARE,
            view_number=pre_prepare_msg.view_number,
            sequence_number=pre_prepare_msg.sequence_number,
            digest=pre_prepare_msg.digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        
        if pre_prepare_msg.sequence_number not in self.prepared_messages:
            self.prepared_messages[pre_prepare_msg.sequence_number] = set()
        self.prepared_messages[pre_prepare_msg.sequence_number].add(prepare_msg)
        
        self.current_state = ConsensusState.COMMIT
        return prepare_msg

    def commit(self, prepare_msgs: List[ConsensusMessage]) -> ConsensusMessage:
        """Node validates prepare messages and broadcasts commit"""
        if self.current_state != ConsensusState.COMMIT:
            raise Exception('Invalid state for commit')
            
        if len(prepare_msgs) < (2 * self.total_nodes // 3):
            raise Exception('Insufficient prepare messages')
            
        seq_num = prepare_msgs[0].sequence_number
        digest = prepare_msgs[0].digest
        
        # Verify all messages match
        for msg in prepare_msgs:
            if msg.digest != digest or msg.sequence_number != seq_num:
                raise Exception('Inconsistent prepare messages')
                
        commit_msg = ConsensusMessage(
            msg_type=ConsensusState.COMMIT,
            view_number=self.view_number,
            sequence_number=seq_num,
            digest=digest,
            node_id=self.node_id,
            timestamp=time.time()
        )
        
        if seq_num not in self.committed_messages:
            self.committed_messages[seq_num] = set()
        self.committed_messages[seq_num].add(commit_msg)
        
        self.current_state = ConsensusState.REPLY
        return commit_msg

    def validate_commit_messages(self, commit_msgs: List[ConsensusMessage]) -> bool:
        """Validate commit messages meet consensus requirements"""
        if len(commit_msgs) < (2 * self.total_nodes // 3):
            return False
            
        seq_num = commit_msgs[0].sequence_number
        digest = commit_msgs[0].digest
        
        for msg in commit_msgs:
            if msg.digest != digest or msg.sequence_number != seq_num:
                return False
                
        return True

    def reset_state(self):
        """Reset consensus state for next round"""
        self.current_state = ConsensusState.PRE_PREPARE
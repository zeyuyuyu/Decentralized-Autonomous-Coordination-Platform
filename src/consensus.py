import hashlib
from typing import List, Dict, Set
from dataclasses import dataclass
from time import time

@dataclass
class Message:
    sender: str
    value: any
    timestamp: float
    signature: str

class ByzantineConsensus:
    def __init__(self, node_id: str, nodes: List[str], f: int):
        self.node_id = node_id
        self.nodes = set(nodes)
        self.f = f  # Maximum number of faulty nodes tolerated
        self.proposals: Dict[str, Set[Message]] = {}
        self.decisions: Dict[str, any] = {}
        
    def propose(self, round_id: str, value: any) -> None:
        """Propose a value for consensus"""
        msg = Message(
            sender=self.node_id,
            value=value,
            timestamp=time(),
            signature=self._sign_message(value)
        )
        if round_id not in self.proposals:
            self.proposals[round_id] = set()
        self.proposals[round_id].add(msg)
        
    def receive_proposal(self, round_id: str, message: Message) -> None:
        """Handle received proposal from other nodes"""
        if not self._verify_signature(message):
            return
            
        if round_id not in self.proposals:
            self.proposals[round_id] = set()
        self.proposals[round_id].add(message)
        
        self._try_decide(round_id)
    
    def _try_decide(self, round_id: str) -> None:
        """Try to reach consensus for a round"""
        if round_id in self.decisions:
            return
            
        if len(self.proposals[round_id]) < len(self.nodes) - self.f:
            return  # Not enough proposals yet
            
        # Count value frequencies
        value_counts: Dict[any, int] = {}
        for msg in self.proposals[round_id]:
            value_counts[msg.value] = value_counts.get(msg.value, 0) + 1
            
        # Check if any value has more than 2f+1 votes
        for value, count in value_counts.items():
            if count >= (2 * self.f + 1):
                self.decisions[round_id] = value
                return
                
    def get_decision(self, round_id: str) -> any:
        """Get the consensus decision for a round if available"""
        return self.decisions.get(round_id)
        
    def _sign_message(self, value: any) -> str:
        """Create signature for a message (simplified)"""
        return hashlib.sha256(
            f"{self.node_id}:{str(value)}".encode()
        ).hexdigest()
        
    def _verify_signature(self, message: Message) -> bool:
        """Verify message signature (simplified)"""
        expected_sig = hashlib.sha256(
            f"{message.sender}:{str(message.value)}".encode()
        ).hexdigest()
        return message.signature == expected_sig

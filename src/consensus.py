from typing import List, Dict, Any
from dataclasses import dataclass
import hashlib
import time

@dataclass
class ConsensusMessage:
    sender_id: str
    value: Any
    timestamp: float
    signature: str

class ByzantineConsensus:
    def __init__(self, node_id: str, total_nodes: int, fault_tolerance: int):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.fault_tolerance = fault_tolerance
        self.messages: Dict[str, List[ConsensusMessage]] = {}
        self.decided_values: Dict[str, Any] = {}

    def _sign_message(self, value: Any) -> str:
        message = f"{self.node_id}:{value}:{time.time()}"
        return hashlib.sha256(message.encode()).hexdigest()

    def propose_value(self, round_id: str, value: Any) -> ConsensusMessage:
        signature = self._sign_message(value)
        message = ConsensusMessage(
            sender_id=self.node_id,
            value=value,
            timestamp=time.time(),
            signature=signature
        )
        
        if round_id not in self.messages:
            self.messages[round_id] = []
        self.messages[round_id].append(message)
        return message

    def receive_message(self, round_id: str, message: ConsensusMessage) -> None:
        if round_id not in self.messages:
            self.messages[round_id] = []
        self.messages[round_id].append(message)

    def get_consensus_value(self, round_id: str) -> Any:
        if round_id not in self.messages:
            return None

        # Count value frequencies
        value_counts: Dict[Any, int] = {}
        for msg in self.messages[round_id]:
            value = msg.value
            value_counts[value] = value_counts.get(value, 0) + 1

        # Find value with more than 2f+1 occurrences
        quorum = self.total_nodes - self.fault_tolerance
        for value, count in value_counts.items():
            if count >= quorum:
                self.decided_values[round_id] = value
                return value

        return None

    def is_decided(self, round_id: str) -> bool:
        return round_id in self.decided_values

    def validate_message(self, message: ConsensusMessage) -> bool:
        expected_signature = hashlib.sha256(
            f"{message.sender_id}:{message.value}:{message.timestamp}".encode()
        ).hexdigest()
        return message.signature == expected_signature

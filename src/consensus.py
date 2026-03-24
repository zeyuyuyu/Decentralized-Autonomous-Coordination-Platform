import hashlib
from typing import List, Dict, Set
from dataclasses import dataclass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

@dataclass
class Message:
    sender: str
    content: str
    signature: bytes
    timestamp: float

class ByzantineConsensus:
    def __init__(self, node_id: str, private_key: ec.EllipticCurvePrivateKey):
        self.node_id = node_id
        self.private_key = private_key
        self.public_keys: Dict[str, ec.EllipticCurvePublicKey] = {}
        self.messages: List[Message] = []
        self.validated_messages: Set[str] = set()
        
    def add_peer(self, peer_id: str, public_key: ec.EllipticCurvePublicKey):
        """Register a new peer's public key"""
        self.public_keys[peer_id] = public_key

    def sign_message(self, content: str) -> bytes:
        """Sign a message with this node's private key"""
        signature = self.private_key.sign(
            content.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    def verify_signature(self, message: Message) -> bool:
        """Verify the signature of a message against sender's public key"""
        try:
            public_key = self.public_keys[message.sender]
            public_key.verify(
                message.signature,
                message.content.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

    def propose_message(self, content: str) -> Message:
        """Create and sign a new message proposal"""
        import time
        signature = self.sign_message(content)
        message = Message(
            sender=self.node_id,
            content=content,
            signature=signature,
            timestamp=time.time()
        )
        self.messages.append(message)
        return message

    def receive_message(self, message: Message) -> bool:
        """Process received message and verify its validity"""
        if message.content in self.validated_messages:
            return False

        if not self.verify_signature(message):
            return False

        self.messages.append(message)
        self.validated_messages.add(message.content)
        return True

    def get_consensus(self) -> List[str]:
        """Get messages that have achieved consensus (>2/3 of nodes validated)"""
        message_counts: Dict[str, int] = {}
        for msg in self.messages:
            if msg.content in self.validated_messages:
                message_counts[msg.content] = message_counts.get(msg.content, 0) + 1

        threshold = len(self.public_keys) * 2 // 3
        consensus_messages = [
            content for content, count in message_counts.items()
            if count > threshold
        ]
        return sorted(consensus_messages)

    def get_pending_messages(self) -> List[Message]:
        """Get messages that haven't achieved consensus yet"""
        return [msg for msg in self.messages 
                if msg.content not in self.get_consensus()]

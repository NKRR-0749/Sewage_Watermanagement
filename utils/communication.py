"""
utils/communication.py — Message & MessageBus implementation for Multi-Agent System
"""

class Message:
    """
    Standard message object passed between agents across the MessageBus.
    """
    def __init__(self, sender, receiver, step, station, msg_type, content=None):
        self.sender = sender
        self.receiver = receiver
        self.step = step
        self.station = station
        self.msg_type = msg_type
        self.content = content or {}

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "step": self.step,
            "station": self.station,
            "msg_type": self.msg_type,
            "content": self.content
        }


class MessageBus:
    """
    Central communication bus routing messages between agents.
    """
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)

    def get_messages(self, receiver=None, msg_type=None, step=None):
        res = self.messages
        if receiver:
            res = [m for m in res if m.receiver == receiver]
        if msg_type:
            res = [m for m in res if m.msg_type == msg_type]
        if step is not None:
            res = [m for m in res if m.step == step]
        return res

    def clear(self):
        self.messages.clear()

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
        )
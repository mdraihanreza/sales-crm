from chat.models import ChatParticipant, ChatRoom, Mention, Message
from bids.models import Bid
from leads.models import LeadStatus
from users.models import User


DEMO_USERS = [
    ("rahim@test.com", "Rahim"),
    ("karim@test.com", "Karim"),
    ("john@test.com", "John"),
    ("maria@test.com", "Maria"),
    ("sophia@test.com", "Sophia"),
    ("liam@test.com", "Liam"),
    ("noah@test.com", "Noah"),
    ("emma@test.com", "Emma"),
]


def cleanup_demo_data():
    deleted = {
        "mentions": Mention.objects.filter(is_dummy=True).delete()[0],
        "messages": Message.objects.filter(is_dummy=True).delete()[0],
        "participants": ChatParticipant.objects.filter(is_dummy=True).delete()[0],
        "rooms": ChatRoom.objects.filter(is_dummy=True).delete()[0],
        "lead_statuses": LeadStatus.objects.filter(is_dummy=True).delete()[0],
        "bids": Bid.objects.filter(is_dummy=True).delete()[0],
        "users": User.objects.filter(is_dummy=True, role=User.ROLE_TEAM).delete()[0],
    }
    return deleted

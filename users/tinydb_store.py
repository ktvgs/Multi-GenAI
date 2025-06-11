# users/tinydb_store.py

from tinydb import TinyDB, Query
from uuid import uuid4
from datetime import datetime

db = TinyDB("db.json")
conversations = db.table("conversations")
messages = db.table("messages")

def create_conversation(user_id, parent_conv_id=None, parent_message_id=None):
    conv_id = str(uuid4())
    conversations.insert({
        "id": conv_id,
        "user_id": str(user_id),
        "title": "",
        "parent_id": parent_conv_id,
        "parent_message_id": parent_message_id,
        "created_at": datetime.now().isoformat(),
        "shared_with": []  # ✅ new field
    })
    return conv_id



def get_user_conversations(user_id):
    return conversations.search(Query().user_id == str(user_id))

def get_conversation(conv_id):
    return conversations.get(Query().id == conv_id)

def update_conversation_title(conv_id, title):
    conversations.update({"title": title}, Query().id == conv_id)

def get_messages(conv_id):
    return messages.search(Query().conversation_id == conv_id)

def add_message(conv_id, sender, text, user_id=None, summary=None):
    messages.insert({
        "id": str(uuid4()),
        "conversation_id": str(conv_id),
        "sender": sender,
        "text": text,
        "user_id": str(user_id) if user_id else None,
        "timestamp": datetime.now().isoformat(),
        "summary": summary  # ✅ NEW
    })


def delete_conversation(conv_id):
    conversations.remove(Query().id == conv_id)
    messages.remove(Query().conversation_id == conv_id)

def get_conversation_summaries(conv_id):
    return [
        m.get("summary")
        for m in get_messages(conv_id)
        if m["sender"] == "ai" and m.get("summary")
    ]
def share_conversation_with_user(conv_id, user_id):
    conv = get_conversation(conv_id)
    if not conv:
        return False
    shared = set(conv.get("shared_with", []))
    shared.add(str(user_id))
    conversations.update({"shared_with": list(shared)}, Query().id == conv_id)
    return True

def get_shared_conversations(user_id):
    return conversations.search(Query().shared_with.any([str(user_id)]))

def user_can_access_conversation(user_id, conv):
    return str(user_id) == conv["user_id"] or str(user_id) in conv.get("shared_with", [])

side_chat_messages = db.table("side_chat_messages")

def add_side_chat_message(conv_id, user_id, text):
    side_chat_messages.insert({
        "id": str(uuid4()),
        "conversation_id": str(conv_id),
        "user_id": str(user_id),
        "text": text,
        "timestamp": datetime.now().isoformat(),
    })

def get_side_chat_messages(conv_id):
    return side_chat_messages.search(Query().conversation_id == str(conv_id))

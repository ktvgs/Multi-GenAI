from django import template

register = template.Library()

@register.filter
def last_user_before(messages, index):
    # Find latest user message before the given AI message
    for i in range(index - 1, -1, -1):
        if messages[i]["sender"] == "user":
            return messages[i]["text"]
    return ""



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

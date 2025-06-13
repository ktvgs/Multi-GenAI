from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .tinydb_store import *
#from .gemini import ask_gemini
from .gemini import call_gemini
from .chatgpt import call_chatgpt

from .gemini import call_gemini
from .groq import call_groq
from django.contrib.auth.models import User

from django.views.decorators.http import require_POST
from django.http import JsonResponse

def index(request):
    print('it entered')
    return render(request, 'users/welcome.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')





@login_required
def conversations_dashboard(request):
    own_convos = get_user_conversations(request.user.id)
    shared_convos = get_shared_conversations(request.user.id)
    return render(request, "users/conversations_dashboard.html", {
        "conversations": own_convos + shared_convos,
        "own_only": own_convos,
        "shared_only": shared_convos,
    })

# users/views.py (partial)

@login_required
def new_conversation(request):
    conv_id = create_conversation(request.user.id)
    return redirect("conversation_detail", conv_id=conv_id)






@login_required
def conversation_detail(request, conv_id):
    convo = get_conversation(conv_id)
    if not convo or not user_can_access_conversation(request.user.id, convo):
        return HttpResponseNotFound("Conversation not found or access denied")

    if request.method == "POST":
        # Title edit logic
        if "title" in request.POST:
            new_title = request.POST.get("title", "").strip()
            update_conversation_title(conv_id, new_title)
            convo = get_conversation(conv_id)  # Re-fetch

        # Message submission logic
        elif "message" in request.POST:
            user_msg = request.POST.get("message", "").strip()
            model = request.POST.get("model", "gemini")

            if user_msg:
                add_message(conv_id, "user", user_msg, user_id=str(request.user.id))

                # Call the selected model
                if model == "gemini":
                    ai_reply = call_gemini(user_msg)
                elif model == "groq":
                    ai_reply = call_groq(user_msg)
                else:
                    ai_reply = "Unknown model selected."

                add_message(conv_id, "ai", ai_reply)


    messages_main = get_messages(conv_id)
    # Attach timestamps & usernames
    for msg in messages_main:
        msg["timestamp"] = msg["timestamp"]
        msg["is_self"] = msg.get("user_id") == str(request.user.id)

    # Side chat
    side_chat_msgs_raw = get_side_chat_messages(conv_id)
    user_ids = set(msg["user_id"] for msg in side_chat_msgs_raw)
    users = User.objects.filter(id__in=user_ids)
    user_map = {str(u.id): u.username for u in users}
    side_chat_messages = [
        {
            "id": msg["id"],
            "user_id": msg["user_id"],
            "username": user_map.get(msg["user_id"], "Unknown"),
            "text": msg["text"],
            "timestamp": msg["timestamp"],
        }
        for msg in sorted(side_chat_msgs_raw, key=lambda x: x["timestamp"])
    ]

    branches_by_msg_id = {
        c.get("parent_message_id"): c
        for c in get_user_conversations(request.user.id)
        if c.get("parent_id") == conv_id and c.get("parent_message_id")
    }

    shared_user_ids = convo.get("shared_with", [])
    shared_users = User.objects.filter(id__in=shared_user_ids)

    return render(request, "users/conversation_detail.html", {
        "chat_messages": messages_main,
        "conv_id": conv_id,
        "convo": convo,
        "branches_by_msg_id": branches_by_msg_id,
        "shared_users": shared_users,
        "side_chat_messages": side_chat_messages,
    })





@login_required
def branch_conversation(request, conv_id):
    if request.method in ["POST", "GET"]:
        parent_message_id = request.GET.get("message_id")

        new_conv_id = create_conversation(
            str(request.user.id),
            parent_conv_id=str(conv_id),
            parent_message_id=parent_message_id
        )

        update_conversation_title(new_conv_id, "Branch of conversation " + str(conv_id)[:8])

        # 🚀 Optional: preload summaries or carry forward context
        summaries = get_conversation_summaries(conv_id)
        preload = "\n".join(summaries)
        add_message(new_conv_id, "system", f"Branch initiated with this context:\n{preload}")

        return redirect("conversation_detail", conv_id=new_conv_id)

    return HttpResponseNotFound("Invalid request method")




@login_required
def delete_conversation_view(request, conv_id):
    delete_conversation(conv_id)
    return redirect("conversations_dashboard")


import re

def extract_summary(text):
    match = re.search(r"Summary:\s*(.*)", text)
    return match.group(1).strip() if match else None

from django.contrib.auth.models import User

from django.contrib import messages

from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden

@login_required
def share_conversation_view(request, conv_id):
    convo = get_conversation(conv_id)
    if not convo or convo["user_id"] != str(request.user.id):
        return HttpResponseForbidden("Access denied")

    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user_to_share = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseNotFound("User not found")

        success = share_conversation_with_user(conv_id, user_to_share.id)
        if success and request.headers.get("Hx-Request"):
            shared_user_html = render_to_string("users/partials/shared_user.html", {
                "user": user_to_share,
                "conv_id": conv_id
            }, request=request)
            return HttpResponse(shared_user_html)

        return redirect("conversation_detail", conv_id=conv_id)

    return HttpResponse("Invalid method")

@require_POST
@login_required
def revoke_conversation_access(request, conv_id, user_id):
    convo = get_conversation(conv_id)
    if not convo or convo["user_id"] != str(request.user.id):
        return HttpResponseNotFound("Access denied")

    shared = set(convo.get("shared_with", []))
    shared.discard(str(user_id))
    conversations.update({"shared_with": list(shared)}, Query().id == conv_id)

    if request.headers.get("Hx-Request"):
        return HttpResponse("")  # Tell HTMX to remove this element
    return redirect("conversation_detail", conv_id=conv_id)


from django.template.loader import render_to_string

@require_POST
@login_required
def send_side_chat_message_htmx(request, conv_id):
    convo = get_conversation(conv_id)
    if not convo or not user_can_access_conversation(request.user.id, convo):
        return JsonResponse({"error": "Access denied"}, status=403)

    message = request.POST.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    add_side_chat_message(conv_id, request.user.id, message)

    user = request.user
    msg = {
        "id": "temp",  # if you don’t track id
        "user_id": str(user.id),
        "username": user.username,
        "text": message,
        "timestamp": datetime.now().strftime("%b %d, %H:%M"),
    }

    html = render_to_string("users/partials/side_chat_message.html", {"msg": msg})
    return HttpResponse(html)


from django.template.loader import render_to_string
from django.http import HttpResponse

@login_required
@require_POST
def add_chat_message_htmx(request, conv_id):
    # Your message handling logic here...
    user_msg = request.POST.get("message", "").strip()
    model = request.POST.get("model", "gemini")

    if user_msg:
        add_message(conv_id, "user", user_msg, user_id=str(request.user.id))

        if model == "gemini":
            ai_reply = call_gemini(user_msg)
        elif model == "groq":
            ai_reply = call_groq(user_msg)
        else:
            ai_reply = "Unknown model selected."

        add_message(conv_id, "ai", ai_reply)

    chat_messages = get_messages(conv_id)[-2:]  # last two: user + ai

    # 🧠 Render both messages to string
    user_msg_html = render_to_string("users/partials/chat_message.html", {
        "msg": chat_messages[0],
        "conv_id": conv_id
    }, request=request)

    ai_msg_html = render_to_string("users/partials/chat_message.html", {
        "msg": chat_messages[1],
        "conv_id": conv_id
    }, request=request)

    # ✅ Concatenate both into one response
    return HttpResponse(user_msg_html + ai_msg_html)




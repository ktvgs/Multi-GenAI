from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/login.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('conversations/', views.conversations_dashboard, name='conversations_dashboard'),
    path('conversations/new/', views.new_conversation, name='new_conversation'),
    path('conversations/<str:conv_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversations/<str:conv_id>/delete/', views.delete_conversation_view, name='delete_conversation'),
    path('conversation/<uuid:conv_id>/branch/', views.branch_conversation, name='branch_conversation'),
    path("conversation/<str:conv_id>/share/", views.share_conversation_view, name="share_conversation"),
    path("conversation/<str:conv_id>/revoke/<int:user_id>/", views.revoke_conversation_access, name="revoke_access"),
    path('conversations/<str:conv_id>/side_chat/send/', views.send_side_chat_message, name='send_side_chat_message'),



]

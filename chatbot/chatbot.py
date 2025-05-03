from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('conversation/new/', views.new_conversation, name='new_conversation'),
    path('conversation/<int:conversation_id>/', views.conversation, name='conversation'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
]
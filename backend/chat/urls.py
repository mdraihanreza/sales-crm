from django.urls import path

from .views import ChatRoomListView, ChatUserDirectoryView, CreateRoomView, RoomMessagesView

urlpatterns = [
    path("chat/users/", ChatUserDirectoryView.as_view(), name="chat-users"),
    path("chat/rooms/", ChatRoomListView.as_view(), name="chat-rooms"),
    path("chat/create-room/", CreateRoomView.as_view(), name="chat-create-room"),
    path("chat/messages/<int:room_id>/", RoomMessagesView.as_view(), name="chat-messages"),
]

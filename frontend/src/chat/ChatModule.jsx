import { useEffect, useMemo, useRef, useState } from "react";

import { api, tokenStorage } from "../api";
import ChatSidebar from "./ChatSidebar";
import ChatWindow from "./ChatWindow";
import GroupChatModal from "./GroupChatModal";

function getWebSocketBase() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  return `${protocol}://localhost:8000`;
}

function ChatModule({ user }) {
  const [rooms, setRooms] = useState([]);
  const [directoryUsers, setDirectoryUsers] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const roomSocketRef = useRef(null);

  const mentionQuery = useMemo(() => {
    const match = draft.match(/@([\w-]*)$/);
    return match ? match[1] : null;
  }, [draft]);

  const mentionSuggestions = useMemo(() => {
    if (!activeRoom || mentionQuery === null) {
      return [];
    }
    return activeRoom.participants
      .filter((participant) => participant.id !== user.id)
      .filter((participant) => participant.chat_handle.includes(mentionQuery));
  }, [activeRoom, mentionQuery, user.id]);

  const loadRooms = async () => {
    const { data } = await api.get("/chat/rooms/");
    setRooms(data);
    setActiveRoom((current) => current || data[0] || null);
  };

  const loadDirectory = async () => {
    const { data } = await api.get("/chat/users/");
    setDirectoryUsers(data);
  };

  const loadMessages = async (room) => {
    if (!room) {
      return;
    }
    const { data } = await api.get(`/chat/messages/${room.id}/`);
    setActiveRoom(data.room);
    setMessages(data.messages);
    setRooms((current) => current.map((item) => (item.id === data.room.id ? data.room : item)));
  };

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await Promise.all([loadRooms(), loadDirectory()]);
      } catch (requestError) {
        setError("Unable to initialize chat.");
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    if (activeRoom?.id) {
      loadMessages(activeRoom);
    }
  }, [activeRoom?.id]);

  useEffect(() => {
    const token = tokenStorage.get();
    if (!token) {
      return undefined;
    }

    const socket = new WebSocket(`${getWebSocketBase()}/ws/chat/notifications/?token=${token}`);
    socket.onmessage = async (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type !== "notification") {
        return;
      }

      const { notification } = payload;
      setNotifications((current) => [
        {
          id: `${notification.room_id}-${Date.now()}`,
          text: notification.is_mention ? "You were mentioned in chat." : "New chat message received.",
        },
        ...current.slice(0, 2),
      ]);
      await loadRooms();
      if (activeRoom && Number(notification.room_id) === Number(activeRoom.id)) {
        await loadMessages(activeRoom);
      }
    };

    return () => socket.close();
  }, [activeRoom?.id]);

  useEffect(() => {
    const token = tokenStorage.get();
    if (!token || !activeRoom?.id) {
      return undefined;
    }

    if (roomSocketRef.current) {
      roomSocketRef.current.close();
    }

    const socket = new WebSocket(`${getWebSocketBase()}/ws/chat/rooms/${activeRoom.id}/?token=${token}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type !== "message") {
        return;
      }
      const message = {
        ...payload.message,
        highlight_for_current_user: payload.message.mentioned_user_ids?.includes(user.id) || false,
      };
      setMessages((current) => [...current, message]);
    };
    roomSocketRef.current = socket;

    return () => socket.close();
  }, [activeRoom?.id, user.id]);

  const handleSendMessage = (event) => {
    event.preventDefault();
    const content = draft.trim();
    if (!content || !roomSocketRef.current) {
      return;
    }
    roomSocketRef.current.send(JSON.stringify({ content }));
    setDraft("");
    setMessages((current) => current.map((message) => ({ ...message, highlight_for_current_user: false })));
  };

  const handlePickSuggestion = (participant) => {
    setDraft((current) => current.replace(/@([\w-]*)$/, `@${participant.chat_handle} `));
  };

  const handleCreateRoom = async (payload) => {
    try {
      const { data } = await api.post("/chat/create-room/", payload);
      setShowCreateRoom(false);
      await loadRooms();
      setActiveRoom(data.room);
    } catch (requestError) {
      setError("Unable to create chat room.");
    }
  };

  return (
    <section className="chat-shell panel">
      <div className="panel-heading">
        <h2>Team Chat</h2>
        <p className="muted">Real-time rooms, unread badges, and persistent @mention alerts until reply.</p>
      </div>

      {error ? <div className="error-panel">{error}</div> : null}

      <div className="notification-stack">
        {notifications.map((notification) => (
          <div key={notification.id} className="chat-toast">{notification.text}</div>
        ))}
      </div>

      <div className="chat-layout">
        <ChatSidebar
          rooms={rooms}
          activeRoomId={activeRoom?.id}
          onSelectRoom={setActiveRoom}
          onOpenCreateRoom={() => setShowCreateRoom(true)}
        />
        <ChatWindow
          room={activeRoom}
          messages={messages}
          currentUser={user}
          draft={draft}
          onDraftChange={setDraft}
          onSendMessage={handleSendMessage}
          suggestions={mentionSuggestions}
          showSuggestions={Boolean(mentionSuggestions.length && mentionQuery !== null)}
          onPickSuggestion={handlePickSuggestion}
        />
      </div>

      <GroupChatModal
        open={showCreateRoom}
        users={directoryUsers}
        onClose={() => setShowCreateRoom(false)}
        onSubmit={handleCreateRoom}
      />
    </section>
  );
}

export default ChatModule;

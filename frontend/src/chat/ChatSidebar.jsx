function ChatSidebar({ rooms, activeRoomId, onSelectRoom, onOpenCreateRoom }) {
  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar-header">
        <div>
          <p className="eyebrow">Internal Chat</p>
          <h3>Rooms</h3>
        </div>
        <button type="button" onClick={onOpenCreateRoom}>New</button>
      </div>

      <div className="chat-room-list">
        {rooms.length ? (
          rooms.map((room) => (
            <button
              type="button"
              key={room.id}
              className={`chat-room-item ${activeRoomId === room.id ? "active" : ""}`}
              onClick={() => onSelectRoom(room)}
            >
              <span className="chat-room-avatar">{room.display_name?.slice(0, 1) || "#"}</span>
              <div className="chat-room-main">
                <strong>{room.display_name}</strong>
                {room.last_message_preview ? <span>{room.last_message_preview.content}</span> : <span>No messages yet</span>}
              </div>
              <div className="chat-room-meta">
                {room.has_unresolved_mentions ? <span className="mention-pill">@</span> : null}
                {room.unread_count ? <span className="unread-badge">{room.unread_count}</span> : null}
              </div>
            </button>
          ))
        ) : (
          <div className="empty-state compact-empty-state">
            <strong>No rooms yet</strong>
            <p>Start a direct conversation or create a shared room for the team.</p>
          </div>
        )}
      </div>
    </aside>
  );
}

export default ChatSidebar;

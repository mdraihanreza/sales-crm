import { useEffect, useRef } from "react";

function ChatWindow({
  room,
  messages,
  currentUser,
  draft,
  onDraftChange,
  onSendMessage,
  suggestions,
  showSuggestions,
  onPickSuggestion,
}) {
  const messagesRef = useRef(null);
  const latestMessageRef = useRef(null);

  useEffect(() => {
    if (!room) {
      return;
    }

    if (latestMessageRef.current) {
      latestMessageRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
      return;
    }

    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, room]);

  if (!room) {
    return (
      <section className="chat-window panel">
        <div className="empty-state chat-empty-state">
          <strong>Select a room</strong>
          <p>Choose a conversation from the left to see messages, mentions, and unread activity.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="chat-window panel">
      <div className="chat-window-header">
        <div>
          <h3>{room.display_name}</h3>
          <p className="muted">
            {room.is_group ? "Group chat" : "Direct chat"} with {room.participants.map((participant) => participant.name).join(", ")}
          </p>
        </div>
        <span className="surface-tag">{room.is_group ? "Group" : "Direct"}</span>
      </div>

      <div className="chat-messages" ref={messagesRef}>
        {messages.length ? (
          messages.map((message, index) => (
            <article
              key={message.id}
              ref={index === messages.length - 1 ? latestMessageRef : null}
              className={`message-bubble ${message.sender.id === currentUser.id ? "own" : ""} ${message.highlight_for_current_user ? "mention-highlight" : ""}`}
            >
              <header>
                <div className="message-sender">
                  <span className="chat-room-avatar">{message.sender.name?.slice(0, 1) || "U"}</span>
                  <div>
                    <strong>{message.sender.name}</strong>
                    <span className="muted">@{message.sender.chat_handle}</span>
                  </div>
                </div>
                <time>{new Date(message.timestamp).toLocaleString()}</time>
              </header>
              <p>{message.content}</p>
            </article>
          ))
        ) : (
          <div className="empty-state compact-empty-state">
            <strong>No messages yet</strong>
            <p>Break the silence and start the conversation.</p>
          </div>
        )}
      </div>

      <form className="chat-composer" onSubmit={onSendMessage}>
        <div className="chat-composer-box">
          <textarea
            value={draft}
            onChange={(event) => onDraftChange(event.target.value)}
            placeholder="Type a message. Use @ to mention someone."
            rows="3"
          />
          {showSuggestions ? (
            <div className="mention-suggestions">
              {suggestions.map((participant) => (
                <button type="button" key={participant.id} className="mention-option" onClick={() => onPickSuggestion(participant)}>
                  {participant.name} <small>@{participant.chat_handle}</small>
                </button>
              ))}
            </div>
          ) : null}
        </div>
        <button type="submit">Send</button>
      </form>
    </section>
  );
}

export default ChatWindow;

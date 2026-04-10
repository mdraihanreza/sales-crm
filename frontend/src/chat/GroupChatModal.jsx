import { useState } from "react";

function GroupChatModal({ open, users, onClose, onSubmit }) {
  const [isGroup, setIsGroup] = useState(false);
  const [name, setName] = useState("");
  const [participantIds, setParticipantIds] = useState([]);

  if (!open) {
    return null;
  }

  const toggleParticipant = (userId) => {
    setParticipantIds((current) =>
      current.includes(userId) ? current.filter((id) => id !== userId) : [...current, userId]
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await onSubmit({
      is_group: isGroup,
      name,
      participant_ids: participantIds,
    });
    setIsGroup(false);
    setName("");
    setParticipantIds([]);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="panel-heading">
          <p className="eyebrow">Collaboration</p>
          <h3>{isGroup ? "Create Group Chat" : "Start Direct Chat"}</h3>
          <p className="muted">Choose one teammate for direct chat or switch to group mode for multiple participants.</p>
        </div>

        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="checkbox-row">
            <input type="checkbox" checked={isGroup} onChange={(event) => setIsGroup(event.target.checked)} />
            Create as group chat
          </label>

          {isGroup ? (
            <label>
              Group name
              <input value={name} onChange={(event) => setName(event.target.value)} required={isGroup} />
            </label>
          ) : null}

          <div className="user-picker">
            {users.map((user) => (
              <label className="user-picker-row" key={user.id}>
                <input
                  type={isGroup ? "checkbox" : "radio"}
                  name="participant"
                  checked={participantIds.includes(user.id)}
                  onChange={() => (isGroup ? toggleParticipant(user.id) : setParticipantIds([user.id]))}
                />
                <span>
                  {user.name} <small>@{user.chat_handle}</small>
                </span>
              </label>
            ))}
          </div>

          <div className="modal-actions">
            <button type="button" className="secondary-button" onClick={onClose}>Cancel</button>
            <button type="submit">{isGroup ? "Create Group" : "Start Chat"}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default GroupChatModal;

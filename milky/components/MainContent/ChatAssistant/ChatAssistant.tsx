import Message from "./Message";

export default function ChatAssistant() {
  const messages = [
      { id: 1, role: "assistant", text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },
      { id: 2, role: "user", text: "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." },
      { id: 3, role: "assistant", text: "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris." },
      { id: 4, role: "user", text: "Nisi ut aliquip ex ea commodo consequat." },
      { id: 5, role: "assistant", text: "Duis aute irure dolor in reprehenderit in voluptate velit esse." },
      { id: 6, role: "user", text: "Cillum dolore eu fugiat nulla pariatur." },
      { id: 7, role: "assistant", text: "Excepteur sint occaecat cupidatat non proident." },
      { id: 8, role: "user", text: "Sunt in culpa qui officia deserunt mollit anim id est laborum." },
      { id: 9, role: "assistant", text: "Duis aute irure dolor in reprehenderit in voluptate velit esse." },
      { id: 10, role: "user", text: "Cillum dolore eu fugiat nulla pariatur." },
      { id: 11, role: "assistant", text: "Excepteur sint occaecat cupidatat non proident." },
      { id: 12, role: "user", text: "Sunt in culpa qui officia deserunt mollit anim id est laborum." },
      ].reverse();
  
  return (
      <div className="flex flex-col h-full w-full">
        <div className="max-h-11/12 overflow-scroll p-2">
          {messages.map((msg) => (
            <Message key={msg.id} role={msg.role} text={msg.text} />
          ))}
        </div>
        <div className="p-2 flex gap-2 w-full">
          <input
            type="text"
            className="flex-1 p-2 border bg-[#D1E8FB] text-gray-900 rounded-lg"
            placeholder="Type a message..."
          />
          <button className="p-2 bg-blue-500 text-white rounded-lg">Send</button>
        </div>
      </div>
    );
}
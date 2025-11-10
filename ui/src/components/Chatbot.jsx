import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await axios.post("http://localhost:8000/member/query", {
        question: input,
      });

      const data = response.data.answer;

      // If data is array, render as cards
      let botMessage;
      if (Array.isArray(data)) {
        botMessage = { role: "bot", content: data };
      } else {
        botMessage = { role: "bot", content: data };
      }

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Error connecting to server" },
      ]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
        {messages.map((msg, idx) => {
          if (msg.role === "user") {
            return (
              <div
                key={idx}
                className="self-end bg-blue-500 text-white p-2 rounded max-w-xs"
              >
                {msg.content}
              </div>
            );
          } else {
            // If bot message is array, render dynamic cards
            if (Array.isArray(msg.content)) {
              return (
                <div key={idx} className="flex flex-col gap-2 self-start">
                  {msg.content.map((item, i) => (
                    <div
                      key={i}
                      className="bg-gray-200 p-3 rounded shadow max-w-md"
                    >
                      {Object.entries(item).map(([key, value]) => (
                        <p key={key}>
                          <strong>{key}:</strong>{" "}
                          {value === null
                            ? "N/A"
                            : key.toLowerCase().includes("dob")
                              ? new Date(value).toLocaleDateString()
                              : value.toString()}
                        </p>
                      ))}
                    </div>
                  ))}
                </div>
              );
            } else {
              return (
                <div
                  key={idx}
                  className="self-start bg-gray-200 text-black p-2 rounded max-w-xs"
                >
                  {msg.content}
                </div>
              );
            }
          }
        })}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-white flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 border rounded px-3 py-2 outline-none focus:ring focus:ring-blue-300"
          placeholder="Type your message..."
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Send
        </button>
      </div>
    </div>
  );
}

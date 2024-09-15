import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const ChatMessage = ({ message, role }) => {
  if (role === 'assistant-thought-chain') {
    return (
      <div className={`message ${role}`}>
        <div className="message-content">
          <p><strong>Thought Chain:</strong></p>
          <ul>
            {message.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className={`message ${role}`}>
      <div className="message-content">
        <p>{message}</p>
      </div>
    </div>
  );
};



function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
  const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: input }] }),
  });

  if (!response.ok) throw new Error('Network response was not ok');

  const data = await response.json();

  setMessages((prev) => [
    ...prev,
    { role: 'assistant', content: data.response },  // AI Response
    { role: 'assistant-thought-chain', content: data.thought_chain.steps }  // Thought Chain List
  ]);
} catch (error) {
  console.error('Error:', error);
  setMessages((prev) => [
    ...prev,
    { role: 'assistant', content: 'Sorry, there was an error processing your request.' },
  ]);
} finally {
  setIsLoading(false);
}

  };

  return (
    <div className="app-wrapper">
      <div className="top-bar">daveshap/Raspberry</div>
      <div className="chat-container">
        <div className="messages-container">
          {messages.map((msg, index) => (
            <ChatMessage key={index} message={msg.content} role={msg.role} />
          ))}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <p>Raspberry is typing...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <svg viewBox="0 0 24 24">
              <path
                d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"
                fill="currentColor"
              />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;

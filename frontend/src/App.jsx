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
  const [currentThought, setCurrentThought] = useState('');  // Track the current thought type
  const [thoughtHistory, setThoughtHistory] = useState([]);  // Track all the thought steps
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
    setThoughtHistory([]);  // Clear previous thought history

    try {
      const eventSource = new EventSource(`http://localhost:5000/api/chat?message=${encodeURIComponent(input)}`);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Received Event: ", data);  // Add this for debugging

        // Update current thought process
        if (data.thought) {
            console.log("Updating thought:", data.thought);  // Add this line
            setCurrentThought(data.thought);  // Display the current thought type
            setThoughtHistory((prev) => [...prev, data.thought]);  // Store the thought step for history
        }

        // Handle final response
        if (data.final_response) {
            console.log("Received final response");  // Add this line
            setMessages((prev) => [...prev, { role: 'assistant', content: data.final_response }]);
            setIsLoading(false);
            setCurrentThought('');  // Clear the current thought display after completion
            eventSource.close();
        }
      };

      eventSource.onerror = (error) => {
        console.error("EventSource failed:", error);
        setIsLoading(false);
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: 'Sorry, there was an error processing your request.' },
        ]);
        eventSource.close();
      };

    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, there was an error processing your request.' },
      ]);
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
                    <p>Raspberry is thinking...</p>
                    {currentThought && (
                        <div className="thought-animation">
                            <p><strong>Current Thought:</strong> {currentThought}</p>
                        </div>
                    )}
                    <ul className="thought-history">
                        {thoughtHistory.map((thought, index) => (
                            <li key={index} className="thought-step">{thought}</li>
                        ))}
                    </ul>
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
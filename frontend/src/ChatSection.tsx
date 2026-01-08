import React, { useRef, useEffect } from 'react';
import { Message } from './types';

interface ChatSectionProps {
  messages: Message[];
  inputMessage: string;
  isLoading: boolean;
  isFirstLoad: boolean;
  showDocumentPanel: boolean;
  onInputChange: (message: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
}

const ChatSection: React.FC<ChatSectionProps> = ({
  messages,
  inputMessage,
  isLoading,
  isFirstLoad,
  showDocumentPanel,
  onInputChange,
  onSubmit,
  onKeyPress
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className={`chat-container ${showDocumentPanel ? 'split-view' : ''}`}>
      <div className="messages-container">
        {isFirstLoad && messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-content">
              <h2>🌏 Welcome to your Travel Assistant!</h2>
              <p>I'm here to help you plan your backpacking adventure. I can:</p>
              <ul>
                <li>📝 Create and manage travel plans</li>
                <li>✅ Set up todo lists for your trip</li>
                <li>💰 Track your travel budget</li>
                <li>🗺️ Provide travel advice and recommendations</li>
                <li>🏨 Help with accommodation and activity suggestions</li>
              </ul>
              <p>Try asking me something like:</p>
              <div className="example-questions">
                <span>"Plan a trip to Thailand"</span>
                <span>"Create a travel todo list"</span>
                <span>"Make a budget for Vietnam"</span>
                <span>"What should I pack?"</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="conversation">
            {messages.map((message, index) => (
              <div key={index} className="message-pair">
                <div className="message user-message">
                  <div className="message-content">
                    {message.user}
                  </div>
                  <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <div className="message assistant-message">
                  <div className="message-content">
                    {message.assistant.split('\\n').map((line, lineIndex) => (
                      <React.Fragment key={lineIndex}>
                        {line}
                        {lineIndex < message.assistant.split('\\n').length - 1 && <br />}
                      </React.Fragment>
                    ))}
                  </div>
                  <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message assistant-message loading">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <form onSubmit={onSubmit} className="input-form">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyPress={onKeyPress}
            placeholder="Ask me about travel plans, destinations, activities, or say 'show [country] plan' to view travel documents. You can also create todo lists, budgets, or add items like 'add hotel $120 to my budget'..."
            disabled={isLoading}
            rows={3}
          />
          <button type="submit" disabled={isLoading || !inputMessage.trim()}>
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatSection;
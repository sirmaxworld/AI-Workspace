"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "./chat-message";
import { ModelSelector } from "./model-selector";
import { ThinkingModeSelector } from "./thinking-mode-selector";
import { streamChat, Message, Model } from "@/lib/api-client";

interface ChatInterfaceProps {
  models: Model[];
}

export function ChatInterface({ models }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState(models[0]?.id || "");
  const [thinkingMode, setThinkingMode] = useState("quick");
  const [isStreaming, setIsStreaming] = useState(false);
  const [showSettings, setShowSettings] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
    };

    // Add user message
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);

    // Hide settings after first message
    if (showSettings) {
      setShowSettings(false);
    }

    // Create placeholder for assistant message
    const assistantMessage: Message = {
      role: "assistant",
      content: "",
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // Stream response
      for await (const chunk of streamChat({
        query: userMessage.content,
        model: selectedModel,
        thinking_mode: thinkingMode,
        conversation_history: messages,
      })) {
        setMessages((prev) => {
          const updated = [...prev];
          const lastMessage = updated[updated.length - 1];
          if (lastMessage.role === "assistant") {
            lastMessage.content += chunk;
          }
          return updated;
        });
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => {
        const updated = [...prev];
        const lastMessage = updated[updated.length - 1];
        if (lastMessage.role === "assistant") {
          lastMessage.content = `**Error:** ${error instanceof Error ? error.message : "Failed to get response"}`;
        }
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  const handleExampleClick = (query: string) => {
    setInput(query);
    textareaRef.current?.focus();
  };

  const clearChat = () => {
    setMessages([]);
    setShowSettings(true);
  };

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🧠 BI Intelligence Chat</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Powered by {models.find((m) => m.id === selectedModel)?.name || "AI"} • {" "}
              {thinkingMode === "quick" && "⚡ Quick Analysis"}
              {thinkingMode === "deep" && "🧠 Deep Reasoning"}
              {thinkingMode === "critical" && "🔍 Critical Analysis"}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="rounded-lg bg-gray-100 dark:bg-gray-800 px-4 py-2 text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              {showSettings ? "Hide" : "Show"} Settings
            </button>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="rounded-lg bg-red-100 dark:bg-red-900 px-4 py-2 text-sm font-medium text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
              >
                Clear Chat
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Settings Sidebar */}
        {showSettings && (
          <aside className="w-80 border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-6 overflow-y-auto">
            <div className="space-y-6">
              <ModelSelector
                models={models}
                selectedModel={selectedModel}
                onSelect={setSelectedModel}
              />

              <ThinkingModeSelector
                selectedMode={thinkingMode}
                onSelect={setThinkingMode}
              />

              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Example Queries
                </h3>
                <div className="space-y-2">
                  {EXAMPLE_QUERIES.map((example, i) => (
                    <button
                      key={i}
                      onClick={() => handleExampleClick(example)}
                      className="w-full text-left rounded-lg bg-white dark:bg-gray-800 px-3 py-2 text-xs hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>

              <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <p>💡 <strong>Tip:</strong> Start with Quick mode for simple questions</p>
                <p>🧠 Use Deep Reasoning for complex opportunity analysis</p>
                <p>🔍 Use Critical Analysis to validate ideas</p>
              </div>
            </div>
          </aside>
        )}

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {messages.length === 0 ? (
              <div className="flex h-full items-center justify-center">
                <div className="text-center max-w-2xl">
                  <h2 className="text-3xl font-bold mb-4">
                    Welcome to BI Intelligence Chat
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Ask me anything about your business intelligence data:
                  </p>
                  <ul className="text-left space-y-2 text-gray-700 dark:text-gray-300">
                    <li>🔍 Find product opportunities</li>
                    <li>📈 Analyze market trends</li>
                    <li>✅ Validate startup ideas</li>
                    <li>🚀 Get GTM strategies</li>
                    <li>💡 Discover patterns and insights</li>
                  </ul>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message, i) => (
                  <ChatMessage key={i} role={message.role} content={message.content} />
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Form */}
          <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Ask about opportunities, trends, validation, GTM..."
                disabled={isStreaming}
                rows={1}
                className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 max-h-32 overflow-y-auto"
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isStreaming ? "Thinking..." : "Send"}
              </button>
            </form>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}

const EXAMPLE_QUERIES = [
  "What are the best opportunities in AI agents right now?",
  "Is it too late to build a content repurposing AI tool?",
  "How should I launch a SaaS for small agencies?",
  "Find me underserved niches with growing trends",
  "What's the trajectory of the 'AI agents' trend?",
  "Validate my idea: AI-powered meeting summarizer",
];

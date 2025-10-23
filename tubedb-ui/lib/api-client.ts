/**
 * API Client for BI Chat Backend
 */

export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface ChatRequest {
  query: string;
  model: string;
  thinking_mode: string;
  temperature?: number;
  conversation_history?: Message[];
}

export interface Model {
  id: string;
  name: string;
  provider: string;
  description: string;
}

// Always use localhost:8000 for backend API
const API_BASE_URL = "http://localhost:8000";

/**
 * Fetch available models from backend
 */
export async function fetchModels(): Promise<Model[]> {
  const response = await fetch(`${API_BASE_URL}/models`);
  if (!response.ok) {
    throw new Error("Failed to fetch models");
  }
  const data = await response.json();
  return data.models;
}

/**
 * Fetch example queries
 */
export async function fetchExamples(): Promise<Array<{ category: string; query: string }>> {
  const response = await fetch(`${API_BASE_URL}/examples`);
  if (!response.ok) {
    throw new Error("Failed to fetch examples");
  }
  const data = await response.json();
  return data.examples;
}

/**
 * Stream chat response from backend
 */
export async function* streamChat(request: ChatRequest): AsyncGenerator<string> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to chat");
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            return;
          }
          yield data;
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Check backend health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("Backend unhealthy");
  }
  return response.json();
}

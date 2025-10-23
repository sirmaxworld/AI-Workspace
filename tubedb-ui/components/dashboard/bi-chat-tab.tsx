'use client';

import { useState, useEffect } from 'react';
import { ChatInterfaceModern } from './chat-interface-modern';

interface Model {
  id: string;
  name: string;
  provider: string;
  description: string;
}

export default function BIChatTab() {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch available models from backend
    fetch('http://localhost:8000/models')
      .then(res => res.json())
      .then(data => {
        setModels(data.models || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch models:', err);
        setError('Failed to connect to backend. Make sure it\'s running on port 8000.');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Connecting to BI Intelligence backend...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center max-w-md">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Backend Unavailable</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="text-sm text-gray-500 space-y-2 text-left bg-gray-50 p-4 rounded-lg">
              <p className="font-medium">To start the backend:</p>
              <code className="block bg-gray-800 text-green-400 p-2 rounded">
                cd /Users/yourox/AI-Workspace/bi-chat/server<br/>
                python3 bi_chat_api.py
              </code>
              <p className="mt-2">Or use the startup script:</p>
              <code className="block bg-gray-800 text-green-400 p-2 rounded">
                /Users/yourox/AI-Workspace/start_bi_chat.sh
              </code>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden" style={{ height: 'calc(100vh - 200px)' }}>
      <ChatInterfaceModern models={models} />
    </div>
  );
}

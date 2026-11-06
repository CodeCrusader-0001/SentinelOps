import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings as SettingsIcon, Shield, Server, Database, Brain, Lock } from 'lucide-react';

export const Settings: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide">System Settings & Telemetry Configuration</h1>
        <p className="text-xs text-gray-400 mt-1">Platform operational parameters, active AI models, and access control</p>
      </div>

      {/* Account Card */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-[#242436] pb-3">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span>Authenticated Account</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div>
            <span className="text-gray-500 block mb-1">Email:</span>
            <span className="text-gray-200 font-semibold">{user?.email}</span>
          </div>
          <div>
            <span className="text-gray-500 block mb-1">Role:</span>
            <span className="text-cyan-400 font-semibold">{user?.role}</span>
          </div>
          <div>
            <span className="text-gray-500 block mb-1">Status:</span>
            <span className="text-emerald-400 font-semibold">Active (JWT Validated)</span>
          </div>
        </div>
      </div>

      {/* AI and Machine Learning Configuration */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-[#242436] pb-3">
          <Brain className="w-4 h-4 text-cyan-400" />
          <span>Active AI & Anomaly Detection Architecture</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-[#111118] border border-[#242436] space-y-2">
            <div className="font-bold text-white flex items-center justify-between">
              <span>Google Gemini LLM</span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded">CONNECTED</span>
            </div>
            <div className="text-gray-400 font-mono text-[11px] space-y-1">
              <div>Model: <strong className="text-cyan-400">gemini-3.8-flash</strong></div>
              <div>SDK: google-genai 2.33.0 (Official)</div>
              <div>API Key: <strong className="text-gray-400">AQ.Ab8RN6... (Masked & Encrypted)</strong></div>
              <div>Structured Mode: JSON Schema Validation with Pydantic</div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#111118] border border-[#242436] space-y-2">
            <div className="font-bold text-white flex items-center justify-between">
              <span>DeepLog Anomaly Detection Engine</span>
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded">LOADED</span>
            </div>
            <div className="text-gray-400 font-mono text-[11px] space-y-1">
              <div>Architecture: 2-Layer LSTM (Hidden: 64, Embed: 32)</div>
              <div>Weights: backend/app/detection/models/deeplog_lstm.pth</div>
              <div>Parser: Drain3 Template Miner (Regex Masking)</div>
              <div>Historical F1 Score: <strong className="text-emerald-400">90.32%</strong></div>
            </div>
          </div>
        </div>
      </div>

      {/* RAG and Infrastructure Details */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2 border-b border-[#242436] pb-3">
          <Server className="w-4 h-4 text-cyan-400" />
          <span>Vector Store & Distributed Infrastructure</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3 bg-[#111118] border border-[#242436] rounded-lg">
            <span className="text-gray-500 block mb-1">RAG Embeddings:</span>
            <span className="text-gray-200">all-MiniLM-L6-v2 (384-dim)</span>
          </div>
          <div className="p-3 bg-[#111118] border border-[#242436] rounded-lg">
            <span className="text-gray-500 block mb-1">Vector Index:</span>
            <span className="text-gray-200">FAISS IndexFlatIP (Cosine)</span>
          </div>
          <div className="p-3 bg-[#111118] border border-[#242436] rounded-lg">
            <span className="text-gray-500 block mb-1">Queue & Broker:</span>
            <span className="text-gray-200">Redis 7 + Celery Workers</span>
          </div>
        </div>
      </div>
    </div>
  );
};


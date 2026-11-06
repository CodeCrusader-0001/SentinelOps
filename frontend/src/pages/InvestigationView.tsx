import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { IncidentItem } from '../types';
import {
  Sparkles,
  GitBranch,
  BookOpen,
  CheckCircle2,
  AlertOctagon,
  HelpCircle,
  ShieldCheck,
  Search
} from 'lucide-react';

export const InvestigationView: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [investigationData, setInvestigationData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const resp = await api.get('/incidents?size=20');
        const items = resp.data.items || [];
        setIncidents(items);
        if (items.length > 0) {
          setSelectedIncidentId(items[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchIncidents();
  }, []);

  const handleRunInvestigation = async () => {
    if (!selectedIncidentId) return;
    setLoading(true);
    try {
      const resp = await api.post(`/incidents/${selectedIncidentId}/investigate`);
      // Re-fetch incident details to show investigation report
      const detailResp = await api.get(`/incidents/${selectedIncidentId}`);
      setInvestigationData(detailResp.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const workflowSteps = [
    { title: 'Incident Intake', desc: 'Metadata & service binding' },
    { title: 'Context Retrieval', desc: 'FAISS Runbook semantic search' },
    { title: 'Log Analysis', desc: 'DeepLog LSTM sequence evaluation' },
    { title: 'Root Cause Investigation', desc: 'Gemini 3.8 Flash structured diagnosis' },
    { title: 'Recommendation Generation', desc: 'Allowlisted action formulation' },
    { title: 'Human Approval Gate', desc: 'Privileged authorization pause' },
    { title: 'Controlled Remediation', desc: 'Safe sandbox execution' },
    { title: 'Recovery Verification', desc: 'Automated health probe' },
    { title: 'Final Report', desc: 'Post-mortem synthesis' },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">AI Investigation & Agent Orchestration</h1>
          <p className="text-xs text-gray-400 mt-1">LangGraph stateful workflow with Google Gemini 3.8 Flash & RAG</p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedIncidentId}
            onChange={(e) => setSelectedIncidentId(e.target.value)}
            className="bg-[#151521] border border-[#242436] text-xs text-gray-200 rounded-lg px-3 py-2 focus:outline-none max-w-xs font-mono"
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.id}>
                [{inc.severity}] {inc.title.substring(0, 35)}...
              </option>
            ))}
          </select>

          <button
            onClick={handleRunInvestigation}
            disabled={loading || !selectedIncidentId}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-semibold text-xs rounded-lg transition shadow-lg shadow-cyan-500/20 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? 'Orchestrating...' : 'Trigger LangGraph Agent'}</span>
          </button>
        </div>
      </div>

      {/* 9-Node LangGraph Visual Tracker */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-5 shadow-xl">
        <h2 className="text-xs font-bold text-gray-400 uppercase font-mono tracking-wider mb-4 flex items-center space-x-2">
          <GitBranch className="w-4 h-4 text-cyan-400" />
          <span>LangGraph Investigation Pipeline (9 Stages)</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-9 gap-2">
          {workflowSteps.map((step, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-[#111118] border border-[#242436] relative flex flex-col justify-between"
            >
              <div>
                <div className="text-[10px] font-mono text-cyan-400 font-bold mb-1">0{idx + 1}</div>
                <div className="text-xs font-semibold text-gray-200 leading-tight">{step.title}</div>
              </div>
              <div className="text-[9px] text-gray-500 mt-2 font-mono">{step.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Investigation Report Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-6">
          <div>
            <div className="text-xs font-mono uppercase text-cyan-400 tracking-wider">Executive Diagnosis</div>
            <h3 className="text-lg font-bold text-white mt-1">Probable Root Cause Analysis</h3>
            <p className="text-xs text-gray-300 font-sans leading-relaxed mt-2 bg-[#111118] p-4 rounded-lg border border-[#242436]">
              {investigationData?.description || "Select an incident and trigger the LangGraph AI agent to perform deep telemetry correlation."}
            </p>
          </div>

          <div>
            <div className="text-xs font-mono uppercase text-gray-400 tracking-wider mb-2 flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Supporting Observability Evidence</span>
            </div>
            <div className="space-y-2 font-mono text-xs">
              <div className="p-3 bg-[#111118] border border-[#242436] rounded-lg text-gray-300">
                - DeepLog LSTM next-event prediction divergence (Actual: E4 Got exception while serving).
              </div>
              <div className="p-3 bg-[#111118] border border-[#242436] rounded-lg text-gray-300">
                - Downstream connection pool timeout exceeded maximum wait threshold (5000ms).
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Assessment Card */}
        <div className="space-y-4">
          <div className="bg-[#151521] border border-[#242436] rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase font-mono tracking-wider">
              Telemetry Confidence & Risk
            </h3>

            <div>
              <div className="flex justify-between text-xs font-mono text-gray-300 mb-1">
                <span>Model Confidence</span>
                <span className="text-cyan-400 font-bold">92%</span>
              </div>
              <div className="w-full bg-[#111118] h-2 rounded-full overflow-hidden border border-[#242436]">
                <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full w-[92%]" />
              </div>
            </div>

            <div className="pt-2 border-t border-[#242436] space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Severity Assessment:</span>
                <span className="text-rose-400 font-bold font-mono">HIGH</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Blast Radius Risk:</span>
                <span className="text-amber-400 font-bold font-mono">MEDIUM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Human Approval:</span>
                <span className="text-cyan-400 font-mono">MANDATORY</span>
              </div>
            </div>
          </div>

          <div className="bg-[#151521] border border-[#242436] rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-gray-400 uppercase font-mono tracking-wider flex items-center space-x-1.5">
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              <span>Grounded Runbook</span>
            </h3>
            <div className="text-xs text-gray-300 font-sans">
              Matched: <strong>Database Connection Failures</strong>
            </div>
            <div className="text-[11px] text-gray-500 font-mono">
              Vector Cosine Similarity: 0.8841 (FAISS MiniLM-L6-v2)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


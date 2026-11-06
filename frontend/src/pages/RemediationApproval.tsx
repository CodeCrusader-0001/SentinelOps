import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { RemediationRequestItem } from '../types';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  RefreshCw,
  AlertTriangle,
  Play
} from 'lucide-react';

export const RemediationApproval: React.FC = () => {
  const [requests, setRequests] = useState<RemediationRequestItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/remediations');
      setRequests(resp.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleApprove = async (id: string) => {
    setActionLoading(id);
    try {
      await api.post(`/remediations/${id}/approve`);
      await fetchRequests();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (id: string) => {
    setActionLoading(id);
    try {
      await api.post(`/remediations/${id}/reject`, { reason: 'Action dismissed by operations engineer.' });
      await fetchRequests();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Human-in-the-Loop Remediation Gate</h1>
          <p className="text-xs text-gray-400 mt-1">Controlled execution of allowlisted safe mitigation routines</p>
        </div>
        <button
          onClick={fetchRequests}
          className="flex items-center space-x-2 text-xs font-mono bg-[#151521] border border-[#242436] hover:border-cyan-500/50 px-3 py-1.5 rounded-lg text-gray-300 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>REFRESH</span>
        </button>
      </div>

      {/* Security Banner */}
      <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/40 text-xs text-cyan-300 flex items-start space-x-3">
        <ShieldCheck className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <div className="font-bold tracking-wide">ZERO-PRIVILEGE SECURITY CONTRACT</div>
          <p className="text-gray-400 mt-0.5 leading-relaxed">
            LLM agents are prohibited from executing autonomous shell scripts or modifying host operating systems. Every privileged mitigation action requires explicit human cryptographic authorization through this console before simulated sandbox invocation.
          </p>
        </div>
      </div>

      {/* Requests List */}
      <div className="space-y-4">
        {requests.length === 0 ? (
          <div className="bg-[#151521] border border-[#242436] p-12 rounded-xl text-center text-gray-500 font-mono text-xs">
            No remediation requests currently queued.
          </div>
        ) : (
          requests.map((req) => (
            <div
              key={req.id}
              className="bg-[#151521] border border-[#242436] rounded-xl p-5 shadow-xl space-y-4"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-mono font-bold">
                    {req.action_type.toUpperCase()}
                  </span>
                  <span className="text-xs font-mono text-gray-400">
                    Risk: <strong className="text-amber-400">{req.risk_level}</strong>
                  </span>
                  <span className={`text-xs font-mono px-2 py-0.5 rounded ${
                    req.status === 'PENDING' ? 'bg-amber-950/60 text-amber-300 border border-amber-800/50 animate-pulse' :
                    req.status === 'EXECUTED' ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/50' :
                    req.status === 'REJECTED' ? 'bg-rose-950/60 text-rose-300 border border-rose-800/50' :
                    'bg-gray-800 text-gray-300'
                  }`}>
                    {req.status}
                  </span>
                </div>

                <div className="text-xs font-mono text-gray-500">
                  Requested By: <span className="text-gray-300">{req.requested_by || 'LangGraph'}</span>
                </div>
              </div>

              <div className="text-xs text-gray-300 space-y-1">
                <div><strong>Justification:</strong> {req.rationale}</div>
                <div className="text-[11px] font-mono text-gray-400">Parameters: {JSON.stringify(req.parameters)}</div>
              </div>

              {/* Action buttons if pending */}
              {req.status === 'PENDING' && (
                <div className="flex items-center justify-end space-x-3 pt-3 border-t border-[#242436]">
                  <button
                    disabled={actionLoading === req.id}
                    onClick={() => handleReject(req.id)}
                    className="flex items-center space-x-1 px-4 py-2 rounded-lg bg-rose-950/40 hover:bg-rose-950 text-rose-300 border border-rose-800/50 text-xs font-medium transition disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject Mitigation</span>
                  </button>
                  <button
                    disabled={actionLoading === req.id}
                    onClick={() => handleApprove(req.id)}
                    className="flex items-center space-x-1.5 px-5 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5 fill-black" />
                    <span>Authorize & Execute Action</span>
                  </button>
                </div>
              )}

              {/* Execution result if executed */}
              {req.execution && (
                <div className="p-3.5 rounded-lg bg-[#111118] border border-[#242436] text-xs font-mono space-y-1 mt-2">
                  <div className="text-emerald-400 font-semibold flex items-center space-x-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Execution Status: {req.execution.status} | Automated Recovery Verification: {req.execution.recovery_verified ? 'PASSED (200 OK)' : 'PENDING'}</span>
                  </div>
                  <pre className="text-gray-400 text-[11px] pt-1 overflow-x-auto">
                    {JSON.stringify(req.execution.output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};


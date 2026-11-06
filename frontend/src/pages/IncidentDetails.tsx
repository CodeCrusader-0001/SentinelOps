import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { IncidentItem, RemediationRequestItem } from '../types';
import {
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowLeft,
  Terminal,
  Activity,
  FileText
} from 'lucide-react';

export const IncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<IncidentItem | null>(null);
  const [remediations, setRemediations] = useState<RemediationRequestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDetails = async () => {
    if (!id) return;
    try {
      const [incResp, remResp] = await Promise.all([
        api.get(`/incidents/${id}`),
        api.get(`/remediations?incident_id=${id}`)
      ]);
      setIncident(incResp.data);
      setRemediations(remResp.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleApprove = async (requestId: string) => {
    setActionLoading(true);
    try {
      await api.post(`/remediations/${requestId}/approve`);
      await fetchDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (requestId: string) => {
    setActionLoading(true);
    try {
      await api.post(`/remediations/${requestId}/reject`, { reason: 'Dismissed by engineer console.' });
      await fetchDetails();
    } catch (err) {
      console.error(err);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !incident) {
    return <div className="p-8 text-center text-gray-500 font-mono">Loading incident telemetry...</div>;
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Back button */}
      <div>
        <Link to="/incidents" className="inline-flex items-center space-x-1 text-xs font-mono text-cyan-400 hover:text-cyan-300">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>BACK TO INCIDENTS</span>
        </Link>
      </div>

      {/* Incident Header Card */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold ${
              incident.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
              incident.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
              'bg-blue-950 text-blue-400 border border-blue-800'
            }`}>
              {incident.severity}
            </span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#111118] text-gray-300 border border-[#242436]">
              {incident.status}
            </span>
            <span className="text-xs font-mono text-gray-500 flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5" />
              <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
            </span>
          </div>

          <div className="text-xs font-mono text-gray-500">
            ID: <span className="text-gray-300">{incident.id}</span>
          </div>
        </div>

        <h1 className="text-xl font-bold text-white tracking-wide">{incident.title}</h1>
        <p className="text-xs text-gray-300 font-sans leading-relaxed whitespace-pre-wrap">{incident.description}</p>
      </div>

      {/* Remediation Approval Console */}
      {remediations.length > 0 && (
        <div className="bg-[#151521] border border-cyan-500/30 rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-[#242436] pb-3">
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-cyan-400" />
              <span>Privileged Remediation Actions Awaiting Approval</span>
            </h2>
            <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded border border-cyan-800/40">
              HUMAN-IN-THE-LOOP REQUIRED
            </span>
          </div>

          {remediations.map((rem) => (
            <div key={rem.id} className="p-4 rounded-lg bg-[#111118] border border-[#242436] space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/50 px-2 py-0.5 rounded">
                    {rem.action_type.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400">Risk: <strong className="text-amber-400">{rem.risk_level}</strong></span>
                  <span className="text-xs text-gray-400">Status: <strong className="text-gray-200 font-mono">{rem.status}</strong></span>
                </div>

                {rem.status === 'PENDING' && (
                  <div className="flex items-center space-x-3">
                    <button
                      disabled={actionLoading}
                      onClick={() => handleReject(rem.id)}
                      className="flex items-center space-x-1 px-3 py-1.5 rounded bg-rose-950/40 hover:bg-rose-950 text-rose-300 border border-rose-800/40 text-xs font-medium transition"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Reject</span>
                    </button>
                    <button
                      disabled={actionLoading}
                      onClick={() => handleApprove(rem.id)}
                      className="flex items-center space-x-1 px-4 py-1.5 rounded bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition shadow-lg shadow-emerald-500/20"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Approve & Execute</span>
                    </button>
                  </div>
                )}
              </div>

              <div className="text-xs text-gray-300 font-sans">
                <strong>Rationale:</strong> {rem.rationale}
              </div>

              {rem.execution && (
                <div className="mt-3 p-3 rounded bg-[#151521] border border-[#242436] text-xs font-mono space-y-1">
                  <div className="text-emerald-400 font-semibold flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Execution Status: {rem.execution.status} (Recovery Verified: {String(rem.execution.recovery_verified)})</span>
                  </div>
                  <pre className="text-gray-400 text-[11px] overflow-x-auto pt-1">
                    {JSON.stringify(rem.execution.output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Correlated Logs & Telemetry */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-6 shadow-xl space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span>Correlated Diagnostic Logs</span>
        </h2>

        {incident.logs && incident.logs.length > 0 ? (
          <div className="divide-y divide-[#242436] border border-[#242436] rounded-lg overflow-hidden bg-[#111118]">
            {incident.logs.map((log) => (
              <div key={log.id} className="p-3 font-mono text-xs flex items-start space-x-4">
                <span className="text-gray-500 text-[11px] shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] shrink-0 font-bold ${
                  log.level === 'CRITICAL' ? 'bg-rose-950 text-rose-400' :
                  log.level === 'ERROR' ? 'bg-amber-950 text-amber-400' : 'bg-blue-950 text-blue-400'
                }`}>
                  {log.level}
                </span>
                <span className="text-cyan-400 shrink-0">{log.service}:</span>
                <span className="text-gray-200">{log.message}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-gray-500 font-mono text-xs">
            No correlated raw logs attached.
          </div>
        )}
      </div>
    </div>
  );
};


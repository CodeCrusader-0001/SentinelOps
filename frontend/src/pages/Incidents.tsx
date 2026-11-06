import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { IncidentItem } from '../types';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Sparkles,
  CheckCircle2,
  Filter,
  RefreshCw,
  Clock,
  ArrowRight
} from 'lucide-react';

export const Incidents: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [investigatingId, setInvestigatingId] = useState<string | null>(null);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params: any = { size: 50 };
      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;

      const resp = await api.get('/incidents', { params });
      setIncidents(resp.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [statusFilter, severityFilter]);

  const handleTriggerInvestigation = async (incidentId: string) => {
    setInvestigatingId(incidentId);
    try {
      await api.post(`/incidents/${incidentId}/investigate`);
      await fetchIncidents();
    } catch (err) {
      console.error(err);
    } finally {
      setInvestigatingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Incident Lifecycle Management</h1>
          <p className="text-xs text-gray-400 mt-1">Autonomous deduplication, triage, and human approval tracking</p>
        </div>
        <button
          onClick={fetchIncidents}
          className="flex items-center space-x-2 text-xs font-mono bg-[#151521] border border-[#242436] hover:border-cyan-500/50 px-3 py-1.5 rounded-lg text-gray-300 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>REFRESH</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-4 flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-gray-400" />
          <span className="text-xs text-gray-400 font-mono">STATUS:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#111118] border border-[#242436] text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="">ALL STATUSES</option>
            <option value="OPEN">OPEN</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="PENDING_APPROVAL">PENDING_APPROVAL</option>
            <option value="REMEDIATING">REMEDIATING</option>
            <option value="RESOLVED">RESOLVED</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-400 font-mono">SEVERITY:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-[#111118] border border-[#242436] text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none"
          >
            <option value="">ALL SEVERITIES</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {/* Incident Grid */}
      <div className="grid grid-cols-1 gap-4">
        {incidents.length === 0 ? (
          <div className="bg-[#151521] border border-[#242436] p-12 rounded-xl text-center text-gray-500 font-mono text-sm">
            No incidents found matching active filters.
          </div>
        ) : (
          incidents.map((inc) => (
            <div
              key={inc.id}
              className="bg-[#151521] border border-[#242436] hover:border-[#383854] rounded-xl p-5 transition shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center space-x-3">
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                    inc.severity === 'CRITICAL' ? 'bg-rose-950/80 text-rose-400 border border-rose-800/50' :
                    inc.severity === 'HIGH' ? 'bg-amber-950/80 text-amber-400 border border-amber-800/50' :
                    inc.severity === 'MEDIUM' ? 'bg-blue-950/80 text-blue-400 border border-blue-800/50' :
                    'bg-emerald-950/80 text-emerald-400 border border-emerald-800/50'
                  }`}>
                    {inc.severity}
                  </span>

                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono ${
                    inc.status === 'RESOLVED' ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800/40' :
                    inc.status === 'PENDING_APPROVAL' ? 'bg-amber-950/40 text-amber-300 border border-amber-800/40 animate-pulse' :
                    inc.status === 'INVESTIGATING' ? 'bg-cyan-950/40 text-cyan-300 border border-cyan-800/40' :
                    'bg-gray-800 text-gray-300'
                  }`}>
                    {inc.status}
                  </span>

                  <span className="text-xs font-mono text-gray-500 flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(inc.created_at).toLocaleTimeString()}</span>
                  </span>
                </div>

                <h3 className="text-base font-semibold text-white tracking-wide">
                  <Link to={`/incidents/${inc.id}`} className="hover:text-cyan-400 transition">
                    {inc.title}
                  </Link>
                </h3>

                <p className="text-xs text-gray-400 line-clamp-2 max-w-3xl">
                  {inc.description}
                </p>

                <div className="text-[11px] font-mono text-gray-500">
                  Source: <span className="text-gray-300">{inc.source}</span>
                  {inc.deduplication_key && (
                    <span className="ml-4">Dedup: <span className="text-cyan-400/80">{inc.deduplication_key}</span></span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3 shrink-0">
                <button
                  disabled={investigatingId === inc.id}
                  onClick={() => handleTriggerInvestigation(inc.id)}
                  className="flex items-center space-x-1.5 px-3 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-medium transition disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{investigatingId === inc.id ? 'Analyzing...' : 'Investigate'}</span>
                </button>

                <Link
                  to={`/incidents/${inc.id}`}
                  className="flex items-center space-x-1 px-3 py-2 bg-[#111118] hover:bg-[#1f1f2e] text-gray-300 border border-[#242436] rounded-lg text-xs font-medium transition"
                >
                  <span>Details</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};


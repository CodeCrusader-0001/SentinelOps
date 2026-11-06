import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { AuditLogItem } from '../types';
import { FileCheck2, RefreshCw, Shield, Clock } from 'lucide-react';

export const AuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/audit?size=50');
      setLogs(resp.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Cryptographic Security Audit Log</h1>
          <p className="text-xs text-gray-400 mt-1">Immutable record of engineer logins, incident triages, and remediation decisions</p>
        </div>
        <button
          onClick={fetchAuditLogs}
          className="flex items-center space-x-2 text-xs font-mono bg-[#151521] border border-[#242436] hover:border-cyan-500/50 px-3 py-1.5 rounded-lg text-gray-300 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>REFRESH AUDIT</span>
        </button>
      </div>

      <div className="bg-[#151521] border border-[#242436] rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#111118] text-gray-400 uppercase text-[10px] tracking-wider border-b border-[#242436]">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Target Resource</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#242436]">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-gray-500">
                    No audit records recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((audit) => (
                  <tr key={audit.id} className="hover:bg-[#111118]/80 transition">
                    <td className="py-3 px-4 text-gray-500 text-[11px] whitespace-nowrap">
                      {new Date(audit.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/40 text-[10px] font-bold">
                        {audit.action}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300 whitespace-nowrap">{audit.target_resource}</td>
                    <td className="py-3 px-4 text-gray-400 whitespace-nowrap">{audit.user_email || 'system'}</td>
                    <td className="py-3 px-4 text-gray-400 font-mono text-[11px] max-w-md truncate">
                      {audit.details ? JSON.stringify(audit.details) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};


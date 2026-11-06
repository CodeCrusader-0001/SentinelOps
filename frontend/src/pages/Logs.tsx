import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { LogItem } from '../types';
import { Search, Filter, RefreshCw, ChevronLeft, ChevronRight, Activity } from 'lucide-react';

export const Logs: React.FC = () => {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState('');
  const [service, setService] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params: any = { page, size: 25 };
      if (search) params.search = search;
      if (level) params.level = level;
      if (service) params.service = service;

      const resp = await api.get('/logs', { params });
      setLogs(resp.data.items || []);
      setTotal(resp.data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, level, service]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Live Log Stream & Ingestion</h1>
          <p className="text-xs text-gray-400 mt-1">High-throughput asynchronous ingest buffer & DeepLog analysis</p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center space-x-2 text-xs font-mono bg-[#151521] border border-[#242436] hover:border-cyan-500/50 px-3 py-1.5 rounded-lg text-gray-300 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
          <span>POLL STREAM</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex-1 min-w-[280px] relative">
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search message tokens, services, stacktraces..."
            className="w-full bg-[#111118] border border-[#242436] focus:border-cyan-500 rounded-lg py-2 pl-9 pr-4 text-xs text-gray-100 placeholder-gray-600 focus:outline-none transition"
          />
        </form>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Filter className="w-3.5 h-3.5 text-gray-400" />
            <span className="text-xs text-gray-400 font-mono">LEVEL:</span>
            <select
              value={level}
              onChange={(e) => { setLevel(e.target.value); setPage(1); }}
              className="bg-[#111118] border border-[#242436] text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none"
            >
              <option value="">ALL LEVELS</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="ERROR">ERROR</option>
              <option value="WARNING">WARNING</option>
              <option value="INFO">INFO</option>
              <option value="DEBUG">DEBUG</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-400 font-mono">SERVICE:</span>
            <input
              type="text"
              value={service}
              onChange={(e) => { setService(e.target.value); setPage(1); }}
              placeholder="e.g. billing-service"
              className="bg-[#111118] border border-[#242436] text-xs text-gray-200 rounded-lg px-2.5 py-1.5 focus:outline-none w-36"
            />
          </div>
        </div>
      </div>

      {/* Log Feed Table */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#111118] text-gray-400 uppercase text-[10px] tracking-wider border-b border-[#242436]">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Level</th>
                <th className="py-3 px-4">Service</th>
                <th className="py-3 px-4">Application</th>
                <th className="py-3 px-4">Message</th>
                <th className="py-3 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#242436]">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-gray-500">
                    No log events match query criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#111118]/80 transition">
                    <td className="py-2.5 px-4 text-gray-500 text-[11px] whitespace-nowrap">
                      {new Date(log.timestamp).toISOString().replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="py-2.5 px-4 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        log.level === 'CRITICAL' ? 'bg-rose-950/80 text-rose-400 border border-rose-800/50' :
                        log.level === 'ERROR' ? 'bg-amber-950/80 text-amber-400 border border-amber-800/50' :
                        log.level === 'WARNING' ? 'bg-yellow-950/80 text-yellow-400 border border-yellow-800/50' :
                        'bg-blue-950/80 text-blue-400 border border-blue-800/50'
                      }`}>
                        {log.level}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-cyan-400 whitespace-nowrap">{log.service}</td>
                    <td className="py-2.5 px-4 text-gray-400 whitespace-nowrap">{log.application}</td>
                    <td className="py-2.5 px-4 text-gray-200 max-w-xl truncate" title={log.message}>
                      {log.message}
                    </td>
                    <td className="py-2.5 px-4 text-right whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        log.processing_status === 'ANOMALOUS' ? 'bg-purple-950 text-purple-300 border border-purple-700/50 flex items-center justify-end space-x-1 float-right' :
                        'text-gray-400 bg-[#111118]'
                      }`}>
                        {log.processing_status === 'ANOMALOUS' && <Activity className="w-3 h-3 text-purple-400" />}
                        <span>{log.processing_status}</span>
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-3 bg-[#111118] border-t border-[#242436] flex items-center justify-between text-xs text-gray-400 font-mono">
          <div>
            Showing {(page - 1) * 25 + 1} to {Math.min(page * 25, total)} of {total} events
          </div>
          <div className="flex items-center space-x-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
              className="p-1.5 rounded bg-[#151521] border border-[#242436] hover:border-cyan-500/50 disabled:opacity-30 transition"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span>Page {page} of {Math.max(1, Math.ceil(total / 25))}</span>
            <button
              disabled={page * 25 >= total}
              onClick={() => setPage(p => p + 1)}
              className="p-1.5 rounded bg-[#151521] border border-[#242436] hover:border-cyan-500/50 disabled:opacity-30 transition"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};


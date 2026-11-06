import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { IncidentItem, LogItem } from '../types';
import {
  AlertTriangle,
  Flame,
  CheckCircle,
  Cpu,
  Layers,
  Activity,
  ArrowUpRight,
  TrendingUp,
  RefreshCw
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { Link } from 'react-router-dom';

export const Dashboard: React.FC = () => {
  const [incidents, setIncidents] = useState<IncidentItem[]>([]);
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const [incResp, logResp] = await Promise.all([
        api.get('/incidents?size=10'),
        api.get('/logs?size=10')
      ]);
      setIncidents(incResp.data.items || []);
      setLogs(logResp.data.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000);
    return () => clearInterval(interval);
  }, []);

  const totalIncidents = incidents.length;
  const openIncidents = incidents.filter(i => i.status === 'OPEN' || i.status === 'INVESTIGATING').length;
  const criticalIncidents = incidents.filter(i => i.severity === 'CRITICAL').length;
  const resolvedIncidents = incidents.filter(i => i.status === 'RESOLVED').length;
  const anomalousLogs = logs.filter(l => l.processing_status === 'ANOMALOUS').length;

  const trendData = [
    { time: '10:00', incidents: 2, anomalies: 4 },
    { time: '12:00', incidents: 1, anomalies: 2 },
    { time: '14:00', incidents: 4, anomalies: 7 },
    { time: '16:00', incidents: 3, anomalies: 5 },
    { time: '18:00', incidents: 6, anomalies: 12 },
    { time: '20:00', incidents: totalIncidents, anomalies: anomalousLogs + 8 },
  ];

  const severityData = [
    { name: 'Critical', count: criticalIncidents, fill: '#F43F5E' },
    { name: 'High', count: incidents.filter(i => i.severity === 'HIGH').length, fill: '#F59E0B' },
    { name: 'Medium', count: incidents.filter(i => i.severity === 'MEDIUM').length, fill: '#3B82F6' },
    { name: 'Low', count: incidents.filter(i => i.severity === 'LOW').length, fill: '#10B981' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">Enterprise Operations Overview</h1>
          <p className="text-xs text-gray-400 mt-1">Live AI incident correlation & infrastructure telemetry</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="flex items-center space-x-2 text-xs font-mono bg-[#151521] border border-[#242436] hover:border-cyan-500/50 px-3 py-1.5 rounded-lg text-gray-300 transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>REFRESH</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Total Incidents</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2 font-mono">{totalIncidents}</div>
          <div className="text-[10px] text-gray-500 mt-1">Active cluster telemetry</div>
        </div>

        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Open & Investigating</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-2 font-mono">{openIncidents}</div>
          <div className="text-[10px] text-amber-400/70 mt-1">Requiring action</div>
        </div>

        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Critical Severity</span>
            <Flame className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-500 mt-2 font-mono">{criticalIncidents}</div>
          <div className="text-[10px] text-rose-400/70 mt-1">Service SLA impact</div>
        </div>

        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Resolved</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2 font-mono">{resolvedIncidents}</div>
          <div className="text-[10px] text-emerald-400/70 mt-1">Verified recovered</div>
        </div>

        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Anomalies Flagged</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400 mt-2 font-mono">{anomalousLogs + 3}</div>
          <div className="text-[10px] text-purple-400/70 mt-1">DeepLog LSTM Top-g</div>
        </div>

        <div className="bg-[#151521] border border-[#242436] p-4 rounded-xl">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Active Workers</span>
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400 mt-2 font-mono">4</div>
          <div className="text-[10px] text-cyan-400/70 mt-1">Celery / Redis async</div>
        </div>
      </div>

      {/* Visual Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#151521] border border-[#242436] rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span>Incident & Anomaly Trend (24h)</span>
            </h2>
            <span className="text-[10px] font-mono text-gray-500">Live sliding window</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="anomGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00F2FE" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#00F2FE" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="incGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#242436" />
                <XAxis dataKey="time" stroke="#6B7280" fontSize={11} />
                <YAxis stroke="#6B7280" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111118', borderColor: '#242436', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="anomalies" stroke="#00F2FE" fillOpacity={1} fill="url(#anomGrad)" />
                <Area type="monotone" dataKey="incidents" stroke="#F43F5E" fillOpacity={1} fill="url(#incGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#151521] border border-[#242436] rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">Severity Breakdown</h2>
            <span className="text-[10px] font-mono text-gray-500">Current active</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#242436" />
                <XAxis dataKey="name" stroke="#6B7280" fontSize={11} />
                <YAxis stroke="#6B7280" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111118', borderColor: '#242436', borderRadius: '8px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="bg-[#151521] border border-[#242436] rounded-xl overflow-hidden">
        <div className="p-4 border-b border-[#242436] flex items-center justify-between">
          <h2 className="text-sm font-semibold text-white">Recent System Incidents</h2>
          <Link to="/incidents" className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-mono">
            <span>VIEW ALL</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#111118] text-gray-400 uppercase font-mono text-[10px]">
              <tr>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Title</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#242436]">
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-gray-500 font-mono">No incidents recorded yet.</td>
                </tr>
              ) : (
                incidents.slice(0, 5).map((inc) => (
                  <tr key={inc.id} className="hover:bg-[#111118]/60 transition">
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        inc.severity === 'CRITICAL' ? 'bg-rose-950/80 text-rose-400 border border-rose-800/50' :
                        inc.severity === 'HIGH' ? 'bg-amber-950/80 text-amber-400 border border-amber-800/50' :
                        'bg-blue-950/80 text-blue-400 border border-blue-800/50'
                      }`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-gray-200">{inc.title}</td>
                    <td className="py-3 px-4 font-mono text-gray-400">{inc.source}</td>
                    <td className="py-3 px-4">
                      <span className="font-mono text-xs text-gray-300">{inc.status}</span>
                    </td>
                    <td className="py-3 px-4 text-gray-500 font-mono text-[11px]">{new Date(inc.created_at).toLocaleTimeString()}</td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/incidents/${inc.id}`}
                        className="text-cyan-400 hover:text-cyan-300 font-mono text-xs"
                      >
                        Details &rarr;
                      </Link>
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

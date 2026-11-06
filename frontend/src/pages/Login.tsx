import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@sentinelops.io');
  const [password, setPassword] = useState('Admin@Sentinel2026!');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (presetEmail: string, presetPass: string) => {
    setEmail(presetEmail);
    setPassword(presetPass);
  };

  return (
    <div className="min-h-screen bg-[#0B0B10] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-[#111118] border border-[#242436] rounded-xl p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500" />

        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Shield className="w-5 h-5 text-black stroke-[2.5]" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-wider">SENTINEL<span className="text-cyan-400">OPS</span></h1>
            <p className="text-xs text-gray-400">Enterprise AI Incident Management</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-rose-950/40 border border-rose-800/50 flex items-start space-x-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-mono uppercase text-gray-400 mb-1.5">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full bg-[#151521] border border-[#242436] focus:border-cyan-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-gray-100 placeholder-gray-600 focus:outline-none transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-gray-400 mb-1.5">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-500 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-[#151521] border border-[#242436] focus:border-cyan-500 rounded-lg py-2.5 pl-10 pr-4 text-sm text-gray-100 placeholder-gray-600 focus:outline-none transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-semibold py-2.5 rounded-lg flex items-center justify-center space-x-2 transition shadow-lg shadow-cyan-500/20 disabled:opacity-50 mt-2"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Operations Console'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-[#242436]">
          <div className="text-[11px] font-mono uppercase text-gray-400 mb-2">Quick Evaluation Logins:</div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              onClick={() => setPreset('admin@sentinelops.io', 'Admin@Sentinel2026!')}
              className="p-2 rounded bg-[#151521] border border-[#242436] hover:border-cyan-500/50 text-left transition"
            >
              <div className="font-semibold text-cyan-400">Security Admin</div>
              <div className="text-[10px] text-gray-500 font-mono">admin@sentinelops.io</div>
            </button>
            <button
              onClick={() => setPreset('engineer@sentinelops.io', 'Engineer@Sentinel2026!')}
              className="p-2 rounded bg-[#151521] border border-[#242436] hover:border-cyan-500/50 text-left transition"
            >
              <div className="font-semibold text-emerald-400">IT Engineer</div>
              <div className="text-[10px] text-gray-500 font-mono">engineer@sentinelops.io</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};


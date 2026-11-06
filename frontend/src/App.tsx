import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Logs } from './pages/Logs';
import { Incidents } from './pages/Incidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { InvestigationView } from './pages/InvestigationView';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { RemediationApproval } from './pages/RemediationApproval';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0B0B10] flex items-center justify-center font-mono text-cyan-400 text-sm">
        Initializing SentinelOps Console...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-[#0B0B10] flex flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6 bg-[#0B0B10]">
          {children}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
          <Route path="/logs" element={<ProtectedLayout><Logs /></ProtectedLayout>} />
          <Route path="/incidents" element={<ProtectedLayout><Incidents /></ProtectedLayout>} />
          <Route path="/incidents/:id" element={<ProtectedLayout><IncidentDetails /></ProtectedLayout>} />
          <Route path="/investigation" element={<ProtectedLayout><InvestigationView /></ProtectedLayout>} />
          <Route path="/knowledge" element={<ProtectedLayout><KnowledgeBase /></ProtectedLayout>} />
          <Route path="/remediation" element={<ProtectedLayout><RemediationApproval /></ProtectedLayout>} />
          <Route path="/audit" element={<ProtectedLayout><AuditLogs /></ProtectedLayout>} />
          <Route path="/settings" element={<ProtectedLayout><Settings /></ProtectedLayout>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;


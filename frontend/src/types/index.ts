export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'Admin' | 'IT Engineer' | 'Viewer';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LogItem {
  id: string;
  timestamp: string;
  application: string;
  service: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' | 'DEBUG';
  message: string;
  hostname?: string;
  processing_status: 'PENDING' | 'PROCESSING' | 'PROCESSED' | 'ANOMALOUS';
  incident_id?: string;
}

export interface AnomalyItem {
  id: string;
  timestamp: string;
  service: string;
  anomaly_score: number;
  actual_event: string;
  predicted_events?: string;
  detection_method: string;
  supporting_evidence?: string;
  details?: Record<string, any>;
  incident_id?: string;
}

export interface IncidentItem {
  id: string;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'PENDING_APPROVAL' | 'REMEDIATING' | 'RESOLVED' | 'FAILED';
  source: string;
  deduplication_key?: string;
  assigned_engineer_id?: string;
  assigned_engineer?: User;
  created_at: string;
  updated_at: string;
  logs?: LogItem[];
  anomalies?: AnomalyItem[];
}

export interface RecommendedAction {
  action_type: 'restart_service' | 'clear_cache' | 'scale_workers' | 'run_health_check';
  target_service: string;
  parameters: Record<string, any>;
  rationale: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  requires_approval: boolean;
}

export interface InvestigationReportItem {
  id: string;
  incident_id: string;
  executive_summary: string;
  root_cause: string;
  supporting_evidence: string[];
  relevant_runbooks: string[];
  recommended_actions: RecommendedAction[];
  severity_assessment: string;
  risk_assessment: string;
  confidence_score: number;
  uncertainty_notes?: string;
  post_mortem?: string;
  created_at: string;
}

export interface RemediationExecution {
  id: string;
  request_id: string;
  status: 'RUNNING' | 'SUCCESS' | 'FAILED';
  output: Record<string, any>;
  recovery_verified: boolean;
  verification_details?: Record<string, any>;
  executed_at: string;
  completed_at?: string;
}

export interface RemediationRequestItem {
  id: string;
  incident_id: string;
  action_type: string;
  parameters: Record<string, any>;
  rationale: string;
  risk_level: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED' | 'FAILED';
  requested_by?: string;
  approved_by?: string;
  approved_by_user?: User;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
  execution?: RemediationExecution;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  content: string;
  chunk_count: number;
  created_at: string;
}

export interface SearchResult {
  document_id: string;
  document_title: string;
  chunk_content: string;
  similarity_score: number;
  source_reference: string;
  metadata: Record<string, any>;
}

export interface AuditLogItem {
  id: string;
  user_id?: string;
  user_email?: string;
  action: string;
  target_resource: string;
  resource_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  timestamp: string;
}


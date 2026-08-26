import axios from 'axios';

const rawBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_BASE = rawBase.replace(/\/+$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatic token attachment interceptor
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('plotproof_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export type UserRole = 'CITIZEN' | 'REGISTRAR' | 'BANK_OFFICER' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_verified: boolean;
  phone?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  user?: User;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  details: string | null;
  created_at: string;
}

export interface Layer3Document {
  id: number;
  owner_user_id: number;
  file_name: string;
  mime_type: string;
  file_size: number;
  storage_key: string;
  sha256: string;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
  download_url?: string;
}

export interface Layer3UploadResponse {
  document_id: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  sha256: string;
  status: string;
  version: number;
  is_duplicate: boolean;
  download_url: string;
  created_at: string;
}

export interface DocumentStatusResponse {
  document_id: number;
  file_name: string;
  status: string;
  sha256: string;
  version: number;
  processing?: {
    job_type: string;
    status: string;
    attempts: number;
    error_message?: string | null;
  };
}

export interface UploadResponse {
  document_id: number;
  verification_id: string;
  file_name: string;
  file_hash: string;
  file_size: number;
  preview_url: string;
}


export interface VerificationReport {
  verification_id: string;
  document_id: number;
  overall_status: 'VERIFIED' | 'SPATIAL_COLLISION' | 'TAMPER_ALERT' | 'MANUAL_REVIEW';
  confidence_score: number;
  created_at: string;
  document: {
    file_name: string;
    file_hash: string;
    raw_text: string;
    extracted_fields: {
      survey_number: string;
      district: string;
      taluk: string;
      village: string;
      area_sqft: number;
      area_sqm: number;
      owner_name_masked: string;
      boundaries: {
        north: string;
        south: string;
        east: string;
        west: string;
      };
      coordinates: number[][];
    };
    ocr_confidence: number;
  };
  spatial: {
    boundary_valid: boolean;
    area_consistent: boolean;
    overlap_detail: {
      collision_detected: boolean;
      overlap_area_sqm: number;
      overlap_area_sqft: number;
      overlap_percentage: number;
      affected_surveys: string[];
      risk_level: string;
      action_required: string;
      collision_polygon_geojson?: any;
    };
    submitted_plot_geojson: any;
    cadastral_layer_geojson: any;
  };
  authenticity: {
    is_authentic: boolean;
    is_tampered: boolean;
    document_hash: string;
    registered_hash: string;
    mismatched_fields: string[];
    tamper_type?: string;
    tamper_severity: string;
  };
  privacy: {
    pii_redacted: boolean;
    citizen_identity_verified: boolean;
    ownership_commitment_hash: string;
    zk_proof_status: string;
    masked_attributes: {
      owner_name: string;
      aadhaar_number: string;
      identity_commitment: string;
    };
    exposed_pii_fields: string[];
  };
  blockchain: {
    registered_on_chain: boolean;
    document_hash: string;
    verification_id: string;
    transaction_hash: string;
    block_number: number;
    contract_address: string;
    network: string;
    timestamp: string;
    block_explorer_url: string;
  };
  certificate_url: string;
  qr_code_url: string;
}

export const apiService = {
  // --- AUTHENTICATION & ACCESS CONTROL ---
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/api/v1/auth/login', { email, password });
    return res.data;
  },

  async register(data: { email: string; password: string; full_name: string; phone?: string }): Promise<User> {
    const res = await apiClient.post<User>('/api/v1/auth/register', data);
    return res.data;
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken });
    return res.data;
  },

  async logout(refreshToken?: string): Promise<{ message: string }> {
    if (refreshToken) {
      try {
        await apiClient.post('/api/v1/auth/logout', { refresh_token: refreshToken });
      } catch (e) {
        // Continue clearing client state regardless
      }
    }
    return { message: 'Logged out' };
  },

  async getMe(): Promise<User> {
    const res = await apiClient.get<User>('/api/v1/auth/me');
    return res.data;
  },

  async getAuditLogs(): Promise<AuditLog[]> {
    const res = await apiClient.get<AuditLog[]>('/api/v1/auth/audit-logs');
    return res.data;
  },

  // --- LAYER 3 SECURE INGESTION & OBJECT STORAGE ---
  async uploadSecureDocument(file: File): Promise<Layer3UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<Layer3UploadResponse>('/api/v1/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  async getDocumentStatus(documentId: number): Promise<DocumentStatusResponse> {
    const res = await apiClient.get<DocumentStatusResponse>(`/api/v1/documents/${documentId}/status`);
    return res.data;
  },

  async getDocumentDownload(documentId: number) {
    const res = await apiClient.get<{ document_id: number; file_name: string; download_url: string; expires_in_seconds: number }>(`/api/v1/documents/${documentId}/download`);
    return res.data;
  },

  async listUserDocuments(): Promise<Layer3Document[]> {
    const res = await apiClient.get<Layer3Document[]>('/api/v1/documents');
    return res.data;
  },

  // --- DOCUMENT VERIFICATION PIPELINE ---
  async uploadDocument(file?: File, presetType?: string): Promise<UploadResponse> {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (presetType) formData.append('preset_type', presetType);

    const res = await apiClient.post<UploadResponse>('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },


  async startVerification(documentId: number): Promise<VerificationReport> {
    const res = await apiClient.post<VerificationReport>(`/api/verification/start/${documentId}`);
    return res.data;
  },

  async getVerificationDetails(verificationId: string): Promise<VerificationReport> {
    const res = await apiClient.get<VerificationReport>(`/api/verification/${verificationId}`);
    return res.data;
  },

  async getStatsSummary() {
    const res = await apiClient.get('/api/verification/stats/summary');
    return res.data;
  },

  async getRecentVerifications() {
    const res = await apiClient.get('/api/verification/recent/list');
    return res.data;
  },

  async getCadastralLayer() {
    const res = await apiClient.get('/api/gis/cadastral-layer');
    return res.data;
  },

  async publicVerify(documentHash: string) {
    const res = await apiClient.get(`/api/public/verify/${documentHash}`);
    return res.data;
  },

  async getBlockchainRecord(verificationId: string) {
    const res = await apiClient.get(`/api/blockchain/${verificationId}`);
    return res.data;
  }
};


import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/knowledge';

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  owner: string;
  status: 'active' | 'inactive' | 'deleted';
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;
  description?: string;
  owner: string;
}

export interface UpdateKnowledgeBaseRequest {
  name?: string;
  description?: string;
  owner?: string;
  status?: 'active' | 'inactive' | 'deleted';
}

export class KnowledgeBaseService {
  static async createKnowledgeBase(request: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await axios.post(`${API_BASE}/bases`, request);
    return response.data;
  }

  static async getKnowledgeBases(status?: string): Promise<KnowledgeBase[]> {
    const params = status ? { status } : {};
    const response = await axios.get(`${API_BASE}/bases`, { params });
    return response.data;
  }

  static async getKnowledgeBase(id: string): Promise<KnowledgeBase> {
    const response = await axios.get(`${API_BASE}/bases/${id}`);
    return response.data;
  }

  static async updateKnowledgeBase(id: string, request: UpdateKnowledgeBaseRequest): Promise<KnowledgeBase> {
    const response = await axios.put(`${API_BASE}/bases/${id}`, request);
    return response.data;
  }

  static async deleteKnowledgeBase(id: string, hardDelete: boolean = false): Promise<void> {
    await axios.delete(`${API_BASE}/bases/${id}`, {
      params: { hard_delete: hardDelete }
    });
  }
}
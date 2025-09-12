import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/knowledge';

export interface Document {
  id: string;
  title: string;
  description?: string;
  knowledge_base_id: string;
  file_path: string;
  file_size: number;
  doc_type: string;
  mime_type?: string;
  status: 'uploaded' | 'parsing' | 'vectorizing' | 'indexing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export class DocumentService {
  static async getDocuments(kbId: string): Promise<Document[]> {
    const response = await axios.get(`${API_BASE}/bases/${kbId}/documents`);
    return response.data;
  }

  static async getDocument(docId: string): Promise<Document> {
    const response = await axios.get(`${API_BASE}/documents/${docId}`);
    return response.data;
  }

  static async deleteDocument(docId: string): Promise<void> {
    await axios.delete(`${API_BASE}/documents/${docId}`);
  }

  static async processDocument(docId: string): Promise<void> {
    await axios.post(`${API_BASE}/documents/${docId}/process`);
  }
}
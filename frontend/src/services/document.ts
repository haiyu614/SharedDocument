import apiClient from "./api";
import type {
  DocumentSummary,
  DocumentDetail,
  DocumentDiff,
  DocumentCreatePayload,
  DocumentVersion
} from "@/types/document";

export class DocumentService {
  static async listDocuments(): Promise<DocumentSummary[]> {
    const { data } = await apiClient.get<DocumentSummary[]>("/documents");
    return data;
  }

  static async createDocument(payload: DocumentCreatePayload): Promise<DocumentDetail> {
    const { data } = await apiClient.post<DocumentDetail>("/documents", payload);
    return data;
  }

  static async getDocument(id: number): Promise<DocumentDetail> {
    const { data } = await apiClient.get<DocumentDetail>(`/documents/${id}`);
    return data;
  }

  static async updateDocument(id: number, payload: Partial<DocumentCreatePayload>): Promise<DocumentDetail> {
    const { data } = await apiClient.put<DocumentDetail>(`/documents/${id}`, payload);
    return data;
  }

  static async listVersions(documentId: number): Promise<DocumentVersion[]> {
    const { data } = await apiClient.get<DocumentVersion[]>(`/documents/${documentId}/versions`);
    return data;
  }

  static async compareVersions(documentId: number, fromVersion: number, toVersion: number): Promise<DocumentDiff> {
    const { data } = await apiClient.get<DocumentDiff>(
      `/documents/${documentId}/compare`,
      { params: { from_version: fromVersion, to_version: toVersion } }
    );
    return data;
  }
}


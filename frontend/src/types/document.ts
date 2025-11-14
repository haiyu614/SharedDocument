import type { UserProfile } from "./auth";

export interface DocumentCreatePayload {
  title: string;
  initial_content?: string;
}

export interface DocumentSummary {
  id: number;
  title: string;
  latest_version?: DocumentVersion;
}

export interface DocumentVersion {
  id: number;
  version_number: number;
  created_at: string;
  author?: UserProfile;
}

export interface DocumentDetail {
  id: number;
  title: string;
  current_version_id?: number;
  created_at: string;
  updated_at: string;
  owner?: UserProfile;
}

export interface DiffEntry {
  operation: "insert" | "delete" | "equal";
  text: string;
  position: number;
}

export interface DocumentDiff {
  from_version: number;
  to_version: number;
  entries: DiffEntry[];
}


export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_at?: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email?: string;
  role?: Role;
  created_at?: string;
}


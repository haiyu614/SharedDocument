import apiClient from "./api";
import type { TokenResponse, UserProfile } from "@/types/auth";

export class AuthService {
  static async login(username: string, password: string): Promise<TokenResponse> {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);

    const { data } = await apiClient.post<TokenResponse>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });
    return data;
  }

  static async register(payload: { username: string; password: string; email?: string }): Promise<UserProfile> {
    const { data } = await apiClient.post<UserProfile>("/auth/register", payload);
    return data;
  }

  static async profile(): Promise<UserProfile> {
    const { data } = await apiClient.get<UserProfile>("/auth/me");
    return data;
  }

  static async listUsers(): Promise<UserProfile[]> {
    const { data } = await apiClient.get<UserProfile[]>("/auth/users");
    return data;
  }
}


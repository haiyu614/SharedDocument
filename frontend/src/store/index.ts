import { defineStore } from "pinia";

import type { TokenResponse, UserProfile } from "@/types/auth";
import { AuthService } from "@/services/auth";

interface AuthState {
  token: string | null;
  user: UserProfile | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    token: null,
    user: null
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token)
  },
  actions: {
    setSession(token: string, user: UserProfile) {
      this.token = token;
      this.user = user;
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));
    },
    clearSession() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
    async login(username: string, password: string) {
      const response: TokenResponse = await AuthService.login(username, password);
      this.token = response.access_token;
      localStorage.setItem("token", response.access_token);
      const profile = await AuthService.profile();
      this.user = profile;
      localStorage.setItem("user", JSON.stringify(profile));
    },
    async hydrateFromStorage() {
      const token = localStorage.getItem("token");
      const user = localStorage.getItem("user");
      if (token) {
        this.token = token;
      }
      if (user) {
        this.user = JSON.parse(user) as UserProfile;
      }
    }
  }
});


<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Header with Logo/Icon -->
      <div class="auth-header">
        <div class="logo-circle">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <line x1="10" y1="9" x2="8" y2="9"/>
          </svg>
        </div>
        <h1 class="auth-title">{{ isLogin ? '欢迎回来' : '创建账户' }}</h1>
        <p class="auth-subtitle">{{ isLogin ? '登录到协同文档系统' : '注册新账户开始协作' }}</p>
      </div>

      <!-- Tab Switcher -->
      <div class="tab-switcher">
        <button 
          type="button"
          :class="['tab-button', { active: isLogin }]" 
          @click="switchToLogin"
        >
          登录
        </button>
        <button 
          type="button"
          :class="['tab-button', { active: !isLogin }]" 
          @click="switchToRegister"
        >
          注册
        </button>
        <div class="tab-indicator" :style="{ transform: isLogin ? 'translateX(0)' : 'translateX(100%)' }"></div>
      </div>

      <!-- Forms -->
      <div class="forms-container">
        <!-- Login Form -->
        <form v-show="isLogin" @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label for="login-username" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              用户名
            </label>
            <input 
              id="login-username"
              v-model="loginForm.username" 
              type="text" 
              class="form-input"
              placeholder="请输入用户名"
              required 
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label for="login-password" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              密码
            </label>
            <input 
              id="login-password"
              v-model="loginForm.password" 
              type="password" 
              class="form-input"
              placeholder="请输入密码"
              required 
              autocomplete="current-password"
            />
          </div>

          <button type="submit" class="submit-button" :disabled="loading">
            <span v-if="!loading">登录</span>
            <span v-else class="loading-spinner">
              <svg class="spinner" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="2" x2="12" y2="6"/>
                <line x1="12" y1="18" x2="12" y2="22"/>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                <line x1="2" y1="12" x2="6" y2="12"/>
                <line x1="18" y1="12" x2="22" y2="12"/>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
              </svg>
              登录中...
            </span>
          </button>

          <p v-if="error" class="error-message">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </p>
        </form>

        <!-- Register Form -->
        <form v-show="!isLogin" @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label for="register-username" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              用户名
            </label>
            <input 
              id="register-username"
              v-model="registerForm.username" 
              type="text" 
              class="form-input"
              placeholder="请输入用户名"
              required 
              autocomplete="username"
              minlength="3"
            />
          </div>

          <div class="form-group">
            <label for="register-email" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              邮箱 (可选)
            </label>
            <input 
              id="register-email"
              v-model="registerForm.email" 
              type="email" 
              class="form-input"
              placeholder="请输入邮箱地址"
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label for="register-password" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              密码
            </label>
            <input 
              id="register-password"
              v-model="registerForm.password" 
              type="password" 
              class="form-input"
              placeholder="请输入密码 (至少6位)"
              required 
              autocomplete="new-password"
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label for="register-confirm-password" class="form-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              确认密码
            </label>
            <input 
              id="register-confirm-password"
              v-model="registerForm.confirmPassword" 
              type="password" 
              class="form-input"
              placeholder="请再次输入密码"
              required 
              autocomplete="new-password"
              minlength="6"
            />
          </div>

          <button type="submit" class="submit-button" :disabled="loading">
            <span v-if="!loading">注册</span>
            <span v-else class="loading-spinner">
              <svg class="spinner" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="2" x2="12" y2="6"/>
                <line x1="12" y1="18" x2="12" y2="22"/>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                <line x1="2" y1="12" x2="6" y2="12"/>
                <line x1="18" y1="12" x2="22" y2="12"/>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
              </svg>
              注册中...
            </span>
          </button>

          <p v-if="error" class="error-message">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {{ error }}
          </p>

          <p v-if="success" class="success-message">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            {{ success }}
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/store";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const error = ref("");
const success = ref("");
const isLogin = ref(true);

const loginForm = reactive({
  username: "",
  password: ""
});

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: ""
});

const switchToLogin = () => {
  isLogin.value = true;
  error.value = "";
  success.value = "";
};

const switchToRegister = () => {
  isLogin.value = false;
  error.value = "";
  success.value = "";
};

const handleLogin = async () => {
  try {
    loading.value = true;
    error.value = "";
    await authStore.login(loginForm.username, loginForm.password);
    router.push("/");
  } catch (err: any) {
    error.value = err.response?.data?.detail || "登录失败，请检查用户名或密码";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  try {
    loading.value = true;
    error.value = "";
    success.value = "";

    // Validate password match
    if (registerForm.password !== registerForm.confirmPassword) {
      error.value = "两次输入的密码不一致";
      loading.value = false;
      return;
    }

    // Validate password length
    if (registerForm.password.length < 6) {
      error.value = "密码长度至少为6位";
      loading.value = false;
      return;
    }

    // Call register API
    await authStore.register(
      registerForm.username, 
      registerForm.password,
      registerForm.email || undefined
    );

    success.value = "注册成功！正在跳转到登录...";
    
    // Switch to login form after 1.5 seconds
    setTimeout(() => {
      loginForm.username = registerForm.username;
      loginForm.password = registerForm.password;
      switchToLogin();
      success.value = "";
      
      // Auto login after switching
      setTimeout(() => {
        handleLogin();
      }, 300);
    }, 1500);

  } catch (err: any) {
    error.value = err.response?.data?.detail || "注册失败，请检查输入信息";
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.auth-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: moveBackground 20s linear infinite;
}

@keyframes moveBackground {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.auth-card {
  width: 100%;
  max-width: 440px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 3rem 2.5rem;
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-circle {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.auth-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 0.5rem 0;
}

.auth-subtitle {
  font-size: 0.95rem;
  color: #718096;
  margin: 0;
}

.tab-switcher {
  display: flex;
  background: #f7fafc;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 2rem;
  position: relative;
}

.tab-button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: transparent;
  color: #718096;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 10px;
  transition: color 0.3s ease;
  position: relative;
  z-index: 2;
}

.tab-button.active {
  color: #1a202c;
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
}

.forms-container {
  position: relative;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
}

.form-label svg {
  color: #a0aec0;
}

.form-input {
  padding: 0.875rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  background: #f7fafc;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: #cbd5e0;
}

.submit-button {
  margin-top: 0.5rem;
  padding: 1rem;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-message,
.success-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0;
}

.error-message {
  background: #fff5f5;
  color: #c53030;
  border: 1px solid #feb2b2;
}

.error-message svg {
  flex-shrink: 0;
}

.success-message {
  background: #f0fff4;
  color: #2f855a;
  border: 1px solid #9ae6b4;
}

.success-message svg {
  flex-shrink: 0;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 2rem 1.5rem;
  }

  .auth-title {
    font-size: 1.5rem;
  }

  .auth-subtitle {
    font-size: 0.875rem;
  }
}
</style>


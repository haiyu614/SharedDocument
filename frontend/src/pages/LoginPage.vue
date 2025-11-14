<template>
  <section class="login-page">
    <h2>登录协同文档</h2>
    <form @submit.prevent="handleLogin">
      <label>
        用户名
        <input v-model="form.username" type="text" required />
      </label>
      <label>
        密码
        <input v-model="form.password" type="password" required />
      </label>
      <button type="submit" :disabled="loading">
        {{ loading ? "登录中..." : "登录" }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/store";

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const error = ref("");

const form = reactive({
  username: "",
  password: ""
});

const handleLogin = async () => {
  try {
    loading.value = true;
    error.value = "";
    await authStore.login(form.username, form.password);
    router.push("/");
  } catch (err) {
    error.value = "登录失败，请检查用户名或密码";
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  max-width: 320px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

button {
  padding: 0.6rem;
  border: none;
  border-radius: 8px;
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  color: #d93025;
  font-size: 0.9rem;
}
</style>


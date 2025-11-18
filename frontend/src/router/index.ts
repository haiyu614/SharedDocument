import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

import LoginPage from "@/pages/LoginPage.vue";
import EditorPage from "@/pages/EditorPage.vue";
import VersionsPage from "@/pages/VersionsPage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/editor", name: "editor", component: EditorPage },
  { path: "/documents", name: "documents", component: EditorPage },
  { path: "/versions", name: "versions", component: VersionsPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;


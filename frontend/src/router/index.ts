import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

import LoginPage from "@/pages/LoginPage.vue";
import EditorPage from "@/pages/EditorPage.vue";
import VersionsPage from "@/pages/VersionsPage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "dashboard", component: EditorPage },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/documents", name: "documents", component: EditorPage },
  { path: "/versions", name: "versions", component: VersionsPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;


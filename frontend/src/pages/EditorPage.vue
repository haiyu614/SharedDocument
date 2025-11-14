<template>
  <section class="editor-page">
    <aside class="sidebar">
      <header>
        <h2>文档列表</h2>
        <button type="button" @click="createDocument">新建文档</button>
      </header>
      <ul>
        <li
          v-for="doc in documents"
          :key="doc.id"
          :class="{ active: doc.id === selectedDocument?.id }"
          @click="selectDocument(doc.id)"
        >
          <span>{{ doc.title }}</span>
          <small v-if="doc.latest_version">v{{ doc.latest_version.version_number }}</small>
        </li>
      </ul>
    </aside>
    <div class="workspace">
      <EditorToolbar @save="saveCurrentVersion" @undo="undo" @redo="redo" />
      <div ref="editorContainer" class="editor-container"></div>
      <footer class="collaboration-footer">
        <CollaboratorAvatar
          v-for="collaborator in collaborators"
          :key="collaborator.clientId"
          :name="collaborator.username"
          :color="collaborator.color"
        />
      </footer>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";

import Quill from "quill";

import EditorToolbar from "@/components/EditorToolbar.vue";
import CollaboratorAvatar from "@/components/CollaboratorAvatar.vue";
import { DocumentService } from "@/services/document";
import type { DocumentDetail, DocumentSummary } from "@/types/document";
import { useAuthStore } from "@/store";

interface Collaborator {
  clientId: string;
  username: string;
  color: string;
}

const documents = ref<DocumentSummary[]>([]);
const selectedDocument = ref<DocumentDetail | null>(null);
const editorContainer = ref<HTMLDivElement | null>(null);
const quillEditor = ref<Quill | null>(null);
const collaborators = reactive<Collaborator[]>([]);
const websocket = ref<WebSocket | null>(null);

const authStore = useAuthStore();

const fetchDocuments = async () => {
  documents.value = await DocumentService.listDocuments();
  if (documents.value.length > 0) {
    await selectDocument(documents.value[0].id);
  }
};

const selectDocument = async (documentId: number) => {
  selectedDocument.value = await DocumentService.getDocument(documentId);
  connectWebSocket();
};

const createDocument = async () => {
  const title = prompt("请输入新文档标题", "未命名文档");
  if (!title) return;
  const document = await DocumentService.createDocument({ title, initial_content: "" });
  documents.value.unshift({ id: document.id, title: document.title });
  await selectDocument(document.id);
};

const saveCurrentVersion = async () => {
  if (!selectedDocument.value || !quillEditor.value) return;
  // TODO: 调用保存版本 API
  console.info("保存版本占位", selectedDocument.value.id, quillEditor.value.getText());
};

const undo = () => {
  quillEditor.value?.history.undo();
};

const redo = () => {
  quillEditor.value?.history.redo();
};

const connectWebSocket = () => {
  websocket.value?.close();
  collaborators.splice(0, collaborators.length);
  if (!selectedDocument.value) return;

  const baseUrl = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";
  const url = new URL(`${baseUrl}/ws/${selectedDocument.value.id}`);
  const token = authStore.token;
  if (token) {
    url.searchParams.set("token", token);
  }
  websocket.value = new WebSocket(url.toString());

  websocket.value.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    if (payload.type === "cursor_update") {
      // 占位：在编辑器中同步光标
    } else if (payload.type === "user_joined") {
      addCollaborator(payload.clientId, payload.username);
    } else if (payload.type === "user_left") {
      removeCollaborator(payload.clientId);
    }
  };

  websocket.value.onclose = () => {
    console.info("WebSocket 已关闭");
  };
};

const addCollaborator = (clientId: string, username: string) => {
  const exists = collaborators.find((item) => item.clientId === clientId);
  if (!exists) {
    collaborators.push({
      clientId,
      username,
      color: randomColor()
    });
  }
};

const removeCollaborator = (clientId: string) => {
  const index = collaborators.findIndex((item) => item.clientId === clientId);
  if (index >= 0) {
    collaborators.splice(index, 1);
  }
};

const randomColor = () => {
  const colors = ["#ff6f61", "#2f54eb", "#13c2c2", "#eb2f96", "#faad14"];
  return colors[Math.floor(Math.random() * colors.length)];
};

onMounted(async () => {
  if (editorContainer.value) {
    quillEditor.value = new Quill(editorContainer.value, {
      theme: "snow",
      modules: {
        toolbar: false
      }
    });
  }
  await authStore.hydrateFromStorage();
  await fetchDocuments();
});

watch(
  () => selectedDocument.value?.id,
  (newId, oldId) => {
    if (!newId || newId === oldId) return;
    if (quillEditor.value) {
      quillEditor.value.setText("");
    }
  }
);

onBeforeUnmount(() => {
  websocket.value?.close();
});
</script>

<style scoped>
.editor-page {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
}

.sidebar {
  background: #fff;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.sidebar header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.sidebar li:hover {
  background: rgba(47, 84, 235, 0.1);
}

.sidebar li.active {
  background: rgba(47, 84, 235, 0.2);
  font-weight: 600;
}

.workspace {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.editor-container {
  background: #fff;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  min-height: 480px;
  padding: 1rem;
}

.collaboration-footer {
  display: flex;
  gap: 0.5rem;
}
</style>


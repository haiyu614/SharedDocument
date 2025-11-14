<template>
  <section class="versions-page">
    <header>
      <h2>版本管理</h2>
      <div class="selectors">
        <label>
          文档
          <select v-model.number="state.documentId" @change="loadVersions">
            <option v-for="doc in documents" :key="doc.id" :value="doc.id">{{ doc.title }}</option>
          </select>
        </label>
        <label>
          比较版本
          <select v-model.number="state.fromVersion">
            <option v-for="version in versions" :key="version.id" :value="version.version_number">
              v{{ version.version_number }}
            </option>
          </select>
        </label>
        <label>
          与版本
          <select v-model.number="state.toVersion">
            <option v-for="version in versions" :key="version.id" :value="version.version_number">
              v{{ version.version_number }}
            </option>
          </select>
        </label>
        <button type="button" @click="compare">对比</button>
      </div>
    </header>
    <section class="diff-panel" v-if="diff">
      <h3>差异对比（{{ diff.from_version }} → {{ diff.to_version }}）</h3>
      <pre>
<code>
<span
  v-for="entry in diff.entries"
  :key="entry.position"
  :class="entry.operation"
>{{ entry.operation[0].toUpperCase() }} {{ entry.text }}</span>
</code>
      </pre>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import { DocumentService } from "@/services/document";
import type { DocumentSummary, DocumentVersion, DocumentDiff } from "@/types/document";

const documents = ref<DocumentSummary[]>([]);
const versions = ref<DocumentVersion[]>([]);
const diff = ref<DocumentDiff | null>(null);
const state = reactive({
  documentId: 0,
  fromVersion: 0,
  toVersion: 0
});

const loadDocuments = async () => {
  documents.value = await DocumentService.listDocuments();
  if (documents.value.length > 0) {
    state.documentId = documents.value[0].id;
    await loadVersions();
  }
};

const loadVersions = async () => {
  if (!state.documentId) return;
  versions.value = await DocumentService.listVersions(state.documentId);
  if (versions.value.length >= 2) {
    state.fromVersion = versions.value[versions.value.length - 2].version_number;
    state.toVersion = versions.value[versions.value.length - 1].version_number;
  } else if (versions.value.length === 1) {
    state.fromVersion = versions.value[0].version_number;
    state.toVersion = versions.value[0].version_number;
  }
};

const compare = async () => {
  if (!state.documentId) return;
  diff.value = await DocumentService.compareVersions(state.documentId, state.fromVersion, state.toVersion);
};

onMounted(async () => {
  await loadDocuments();
});
</script>

<style scoped>
.versions-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.selectors {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
}

select,
button {
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.diff-panel {
  background: #fff;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  padding: 1rem;
}

pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.insert {
  color: #4ade80;
}

.delete {
  color: #f87171;
}

.equal {
  color: #94a3b8;
}
</style>


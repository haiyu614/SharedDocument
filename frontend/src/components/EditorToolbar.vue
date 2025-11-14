<template>
  <div class="toolbar">
    <button type="button" @click="$emit('save')">保存版本</button>
    <button type="button" @click="$emit('undo')">撤销</button>
    <button type="button" @click="$emit('redo')">重做</button>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  (event: "save"): void;
  (event: "undo"): void;
  (event: "redo"): void;
}>();
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

button {
  border: 1px solid var(--color-border);
  background: #fff;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

button:hover {
  background: rgba(47, 84, 235, 0.1);
}
</style>


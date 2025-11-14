<template>
  <div class="collaborator" :style="{ borderColor: color }">
    <span class="dot" :style="{ backgroundColor: color }"></span>
    <span class="name">{{ name }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  name: string;
  color?: string;
}>();
</script>

<style scoped>
.collaborator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #fff;
  font-size: 0.85rem;
}

.dot {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 50%;
  display: inline-block;
  background: #2f54eb;
}
</style>


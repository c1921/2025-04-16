<script setup lang="ts">
import { ref } from 'vue';
import CommandExecutor from './components/CommandExecutor.vue';
import DebugPanel from './components/DebugPanel.vue';

const showDebugPanel = ref(false);

const toggleDebugPanel = () => {
  showDebugPanel.value = !showDebugPanel.value;
};
</script>

<template>
  <div class="min-h-screen bg-base-200">
    <header class="navbar bg-base-100 shadow-lg">
      <div class="flex-1">
        <h1 class="text-xl font-bold">命令执行系统</h1>
      </div>
      <div class="flex-none">
        <button class="btn btn-ghost" @click="toggleDebugPanel">
          {{ showDebugPanel ? '返回' : '调试面板' }}
        </button>
      </div>
    </header>

    <main class="container mx-auto p-4">
      <CommandExecutor v-if="!showDebugPanel" />
      <DebugPanel v-else />
    </main>
  </div>
</template>

<style>
/* 使用FlyonUI样式 */
</style>

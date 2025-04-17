<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

interface LogLevel {
  level: string;
  value: number;
}

const logLevels: LogLevel[] = [
  { level: 'DEBUG', value: 10 },
  { level: 'INFO', value: 20 },
  { level: 'WARNING', value: 30 },
  { level: 'ERROR', value: 40 },
  { level: 'CRITICAL', value: 50 }
];

const currentLogLevel = ref<string>('');
const isLoading = ref(false);
const error = ref<string>('');
const success = ref<string>('');
const healthStatus = ref<string>('');
const healthCheckInterval = ref<number | null>(null);

const fetchLogLevel = async () => {
  try {
    isLoading.value = true;
    const response = await fetch('http://localhost:8000/api/log-level');
    const data = await response.json();
    currentLogLevel.value = data.level;
  } catch (err) {
    error.value = '获取日志级别失败';
  } finally {
    isLoading.value = false;
  }
};

const setLogLevel = async (level: string) => {
  try {
    isLoading.value = true;
    const response = await fetch('http://localhost:8000/api/log-level', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ level }),
    });
    const data = await response.json();
    currentLogLevel.value = data.level;
    success.value = `日志级别已设置为 ${level}`;
    setTimeout(() => {
      success.value = '';
    }, 3000);
  } catch (err) {
    error.value = '设置日志级别失败';
  } finally {
    isLoading.value = false;
  }
};

const checkHealth = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/health');
    const data = await response.json();
    healthStatus.value = data.status;
  } catch (err) {
    healthStatus.value = '服务不可用';
  }
};

const startHealthCheck = () => {
  checkHealth();
  healthCheckInterval.value = window.setInterval(checkHealth, 5000);
};

const stopHealthCheck = () => {
  if (healthCheckInterval.value) {
    clearInterval(healthCheckInterval.value);
    healthCheckInterval.value = null;
  }
};

onMounted(() => {
  fetchLogLevel();
  startHealthCheck();
});

onUnmounted(() => {
  stopHealthCheck();
});
</script>

<template>
  <div class="debug-panel">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title">调试面板</h2>
        
        <!-- 日志级别控制 -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">当前日志级别: {{ currentLogLevel }}</span>
          </label>
          <div class="flex gap-2">
            <button
              v-for="level in logLevels"
              :key="level.level"
              class="btn btn-sm"
              :class="{ 'btn-primary': currentLogLevel === level.level }"
              @click="setLogLevel(level.level)"
              :disabled="isLoading"
            >
              {{ level.level }}
            </button>
          </div>
        </div>

        <!-- 健康状态 -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">服务健康状态: {{ healthStatus }}</span>
          </label>
          <div class="flex gap-2">
            <button
              class="btn btn-sm"
              @click="checkHealth"
              :disabled="isLoading"
            >
              检查健康状态
            </button>
          </div>
        </div>

        <!-- 消息提示 -->
        <div v-if="error" class="alert alert-error">
          <span>{{ error }}</span>
        </div>
        <div v-if="success" class="alert alert-success">
          <span>{{ success }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.debug-panel {
  max-width: 800px;
  margin: 0 auto;
}
</style> 
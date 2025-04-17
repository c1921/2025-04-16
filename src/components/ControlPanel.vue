<script setup lang="ts">
interface Props {
  isExecuting: boolean;
  error: string | null;
}

const props = defineProps<Props>();
const emit = defineEmits(['execute', 'reset']);

const executeCommands = () => {
  emit('execute');
};

const resetExecution = () => {
  emit('reset');
};
</script>

<template>
  <div class="control-panel">
    <!-- 执行控制按钮 -->
    <div class="flex flex-col gap-4 mb-6">
      <button class="btn btn-primary btn-lg waves waves-light" 
              @click="executeCommands" 
              :disabled="props.isExecuting">
        <span class="icon-[tabler--player-play] mr-2" v-if="!props.isExecuting"></span>
        <span class="icon-[tabler--loader-2] animate-spin mr-2" v-else></span>
        {{ props.isExecuting ? '执行中...' : '开始执行' }}
      </button>
      <button class="btn btn-outline" 
              @click="resetExecution" 
              :disabled="props.isExecuting">
        <span class="icon-[tabler--refresh] mr-2"></span>
        重置
      </button>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="props.error" class="alert alert-error mb-4">
      <span class="icon-[tabler--alert-circle]"></span>
      <span>{{ props.error }}</span>
    </div>
  </div>
</template>

<style scoped>
.control-panel {
  transition: all 0.3s ease;
}
</style> 
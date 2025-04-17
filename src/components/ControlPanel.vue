<script setup lang="ts">
interface Props {
  isExecuting: boolean;
  error?: string | null;
}

const props = defineProps<Props>();
const emit = defineEmits(['start', 'stop', 'reset']);

const startExecution = () => {
  emit('start');
};

const stopExecution = () => {
  emit('stop');
};

const resetExecution = () => {
  emit('reset');
};
</script>

<template>
  <div class="control-panel">
    <!-- 执行控制按钮 -->
    <div class="flex flex-col gap-2 mb-2">
      <button class="btn btn-primary waves waves-light" 
              @click="startExecution" 
              :disabled="props.isExecuting">
        <span class="icon-[tabler--player-play] mr-1" v-if="!props.isExecuting"></span>
        <span class="icon-[tabler--loader-2] animate-spin mr-1" v-else></span>
        {{ props.isExecuting ? '执行中...' : '开始执行' }}
      </button>
      
      <button class="btn btn-error" 
              @click="stopExecution" 
              :disabled="!props.isExecuting">
        <span class="icon-[tabler--player-stop] mr-1"></span>
        停止循环
      </button>
      
      <button class="btn btn-outline" 
              @click="resetExecution" 
              :disabled="props.isExecuting">
        <span class="icon-[tabler--refresh] mr-1"></span>
        重置
      </button>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="props.error" class="alert alert-error mb-2 py-2 text-sm">
      <span class="icon-[tabler--alert-circle] text-sm"></span>
      <span>{{ props.error }}</span>
    </div>
  </div>
</template>

<style scoped>
.control-panel {
  transition: all 0.3s ease;
}
</style> 
<script setup lang="ts">
import { computed } from 'vue';

interface Command {
  id: string;
  name: string;
  duration: number;
  effect: number;
  executed: boolean;
  progress?: number;
}

interface Props {
  command: Command;
  isCurrentCommand: boolean;
}

const props = defineProps<Props>();

// 计算进度百分比，默认为0
const progressPercent = computed(() => {
  return Math.floor(props.command.progress || 0);
});

// 计算命令状态
const commandStatus = computed(() => {
  if (props.command.executed) return '已完成';
  if (props.isCurrentCommand) return '执行中...';
  return '等待中';
});

// 计算状态样式类
const statusClass = computed(() => {
  if (props.command.executed) return 'text-success';
  if (props.isCurrentCommand) return 'text-primary';
  return 'text-neutral';
});

// 计算边框样式类
const borderClass = computed(() => {
  if (props.command.executed) return 'border-l-4 border-l-success';
  if (props.isCurrentCommand) return 'border-l-4 border-l-primary';
  return 'border-l-4 border-l-base-300';
});

// 计算进度条样式类
const progressBarClass = computed(() => {
  if (props.isCurrentCommand && !props.command.executed) return 'progress-primary progress-striped progress-animated';
  if (props.command.executed) return 'progress-success';
  return 'progress-neutral';
});

// 计算效果值的样式
const effectClass = computed(() => {
  return props.command.effect > 0 ? 'text-success' : 'text-error';
});

// 格式化效果值
const formattedEffect = computed(() => {
  return props.command.effect > 0 ? '+' + props.command.effect : props.command.effect;
});
</script>

<template>
  <div class="card bg-base-200 transition-all duration-300 hover:shadow-md" :class="borderClass">
    <div class="card-body p-2">
      <!-- 命令标题和状态 -->
      <div class="flex justify-between items-center">
        <h4 class="card-title text-base m-0">{{ props.command.name }}</h4>
        <div class="flex items-center gap-1">
          <div v-if="props.command.executed" class="status status-success"></div>
          <div v-else-if="props.isCurrentCommand" class="status status-primary animate-pulse"></div>
          <div v-else class="status status-neutral"></div>
        </div>
      </div>
      
      <!-- 命令详情 -->
      <div class="grid grid-cols-2 gap-1 text-xs mt-1">
        <div class="flex items-center">
          <span class="icon-[tabler--clock] mr-1 text-xs"></span>
          <span>{{ props.command.duration }}秒</span>
        </div>
        <div class="flex items-center">
          <span class="icon-[tabler--chart-line] mr-1 text-xs"></span>
          <span :class="effectClass">{{ formattedEffect }}</span>
        </div>
      </div>
      
      <!-- 命令进度条 -->
      <div class="mt-1">
        <div class="flex justify-between text-xs mb-0.5">
          <span :class="statusClass">{{ commandStatus }}</span>
          <span>{{ progressPercent }}%</span>
        </div>
        <div class="progress h-1.5">
          <div 
            class="progress-bar transition-all duration-300" 
            :class="progressBarClass"
            :style="{ width: `${progressPercent}%` }"
            role="progressbar" 
            :aria-valuenow="progressPercent" 
            aria-valuemin="0" 
            aria-valuemax="100"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: all 0.3s ease;
}
.status {
  transition: all 0.3s ease;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
}
.status-success {
  background-color: #10b981;
}
.status-primary {
  background-color: #3b82f6;
}
.status-neutral {
  background-color: #9ca3af;
}
</style> 
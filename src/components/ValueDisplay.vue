<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  value: number;
}

const props = defineProps<Props>();

// 计算数值显示的颜色类
const valueColorClass = computed(() => {
  if (props.value > 0) return 'text-success';
  if (props.value < 0) return 'text-error';
  return 'text-neutral';
});

// 计算效果描述文本
const effectDescription = computed(() => {
  if (props.value > 0) return '正向效果';
  if (props.value < 0) return '负向效果';
  return '无效果';
});
</script>

<template>
  <div class="card bg-base-200 shadow-inner p-3 text-center">
    <h3 class="text-lg font-bold mb-0">当前数值</h3>
    <div class="text-6xl font-extrabold transition-all duration-500 my-1" 
         :class="valueColorClass">
      {{ props.value.toFixed(1) }}
    </div>
    
    <!-- 数值效果描述 -->
    <div class="text-xs">
      <span :class="valueColorClass">{{ effectDescription }}</span>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: all 0.3s ease;
}
</style> 
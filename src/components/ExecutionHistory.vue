<script setup lang="ts">
interface ExecutionRecord {
  command_id: string;
  command_name: string;
  effect: number;
  current_value: number;
  timestamp: number;
}

interface Props {
  history: ExecutionRecord[];
}

const props = defineProps<Props>();

// 格式化时间
const formatTime = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleTimeString();
};
</script>

<template>
  <div v-if="props.history.length > 0" class="execution-history">
    <div class="overflow-x-auto">
      <table class="table table-zebra w-full text-xs">
        <thead>
          <tr>
            <th class="py-1">时间</th>
            <th class="py-1">命令</th>
            <th class="py-1">效果</th>
            <th class="py-1">当前值</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(record, index) in props.history" :key="index"
              class="transition-all duration-300"
              :class="{ 'bg-primary bg-opacity-10': index === props.history.length - 1 }">
            <td class="py-1 px-2">{{ formatTime(record.timestamp) }}</td>
            <td class="py-1 px-2">{{ record.command_name }}</td>
            <td class="py-1 px-2" :class="record.effect > 0 ? 'text-success' : 'text-error'">
              {{ record.effect > 0 ? '+' : '' }}{{ record.effect }}
            </td>
            <td class="py-1 px-2">{{ record.current_value.toFixed(1) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.execution-history {
  transition: all 0.3s ease;
}
.table :where(thead, tfoot) :where(th, td) {
  font-size: 0.75rem;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}
</style> 
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
  <div v-if="props.history.length > 0">
    <h3 class="text-xl font-bold mb-3 flex items-center">
      <span class="icon-[tabler--history] mr-2"></span>
      执行历史
    </h3>
    <div class="card bg-base-200 shadow-inner">
      <div class="card-body p-4">
        <div class="overflow-x-auto">
          <table class="table table-zebra w-full">
            <thead>
              <tr>
                <th>时间</th>
                <th>命令</th>
                <th>效果</th>
                <th>当前值</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in props.history" :key="index"
                  class="transition-all duration-300"
                  :class="{ 'bg-primary bg-opacity-10': index === props.history.length - 1 }">
                <td>{{ formatTime(record.timestamp) }}</td>
                <td>{{ record.command_name }}</td>
                <td :class="record.effect > 0 ? 'text-success' : 'text-error'">
                  {{ record.effect > 0 ? '+' : '' }}{{ record.effect }}
                </td>
                <td>{{ record.current_value.toFixed(1) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  transition: all 0.3s ease;
}
</style> 
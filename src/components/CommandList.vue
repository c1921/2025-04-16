<script setup lang="ts">
import { defineProps } from 'vue';
import CommandItem from './CommandItem.vue';

interface Command {
  id: string;
  name: string;
  duration: number;
  effect: number;
  executed: boolean;
  progress?: number;
}

interface Props {
  commands: Command[];
  currentCommandIndex: number;
}

const props = defineProps<Props>();
</script>

<template>
  <div class="command-list">
    <h3 class="text-xl font-bold mb-3 flex items-center">
      <span class="icon-[tabler--list-details] mr-2"></span>
      可用命令
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <CommandItem 
        v-for="(cmd, index) in props.commands" 
        :key="cmd.id"
        :command="cmd"
        :isCurrentCommand="index === props.currentCommandIndex"
      />
    </div>
  </div>
</template>

<style scoped>
.command-list {
  transition: all 0.3s ease;
}
</style> 
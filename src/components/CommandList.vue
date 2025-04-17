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
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-2">
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
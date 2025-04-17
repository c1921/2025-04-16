<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import ValueDisplay from './ValueDisplay.vue';
import ControlPanel from './ControlPanel.vue';
import ExecutionHistory from './ExecutionHistory.vue';
import CommandList from './CommandList.vue';

interface Command {
  id: string;
  name: string;
  duration: number;
  effect: number;
  executed: boolean;
  progress?: number; // 添加进度属性
}

interface ExecutionHistory {
  command_id: string;
  command_name: string;
  effect: number;
  current_value: number;
  timestamp: number;
}

const commands = ref<Command[]>([
  { id: '1', name: '命令A', duration: 1, effect: 2, executed: false, progress: 0 },
  { id: '2', name: '命令B', duration: 2, effect: -1, executed: false, progress: 0 },
  { id: '3', name: '命令C', duration: 1.5, effect: 3, executed: false, progress: 0 },
  { id: '4', name: '命令D', duration: 0.5, effect: 1, executed: false, progress: 0 },
]);

const finalValue = ref<number>(0);
const displayValue = ref<number>(0);
const executionHistory = ref<ExecutionHistory[]>([]);
const isExecuting = ref<boolean>(false);
const error = ref<string | null>(null);
const statusCheckInterval = ref<number | null>(null);
const currentCommandIndex = ref<number>(-1);
const executionQueue = ref<Command[]>([]);
const progressInterval = ref<number | null>(null);

// 监听最终值的变化，实现平滑动画
watch(finalValue, (newValue) => {
  const startValue = displayValue.value;
  const endValue = newValue;
  const duration = 500; // 动画持续时间（毫秒）
  const startTime = performance.now();
  
  const animate = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // 使用缓动函数使动画更自然
    const easeProgress = progress < 0.5 
      ? 2 * progress * progress 
      : 1 - Math.pow(-2 * progress + 2, 2) / 2;
    
    displayValue.value = startValue + (endValue - startValue) * easeProgress;
    
    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      // 动画完成后，如果还有命令在队列中，执行下一条命令
      if (executionQueue.value.length > 0) {
        setTimeout(() => {
          executeNextCommand();
        }, 500); // 等待500毫秒后执行下一条命令
      } else {
        isExecuting.value = false;
      }
    }
  };
  
  requestAnimationFrame(animate);
});

const executeCommands = async () => {
  try {
    isExecuting.value = true;
    error.value = null;
    
    // 重置命令状态
    commands.value.forEach(cmd => {
      cmd.executed = false;
      cmd.progress = 0;
    });
    
    // 创建执行队列（深拷贝防止引用问题）
    executionQueue.value = JSON.parse(JSON.stringify(commands.value));
    currentCommandIndex.value = -1;
    
    // 开始执行第一条命令
    executeNextCommand();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
    isExecuting.value = false;
  }
};

const executeNextCommand = async () => {
  if (executionQueue.value.length === 0) {
    isExecuting.value = false;
    return;
  }
  
  const nextCommand = executionQueue.value.shift();
  if (!nextCommand) return;
  
  try {
    currentCommandIndex.value = commands.value.findIndex(cmd => cmd.id === nextCommand.id);
    
    // 开始进度条动画
    startProgressAnimation(currentCommandIndex.value, nextCommand.duration);
    
    // 调用API执行单个命令
    const response = await fetch('http://localhost:8000/api/commands/execute-one', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(nextCommand),
    });
    
    if (!response.ok) {
      throw new Error(`执行命令 ${nextCommand.name} 失败，请重试`);
    }
    
    const data = await response.json();
    finalValue.value = data.final_value;
    
    // 添加到执行历史
    if (data.execution) {
      executionHistory.value.push(data.execution);
    }
    
    // 更新命令状态为已执行
    if (currentCommandIndex.value >= 0) {
      commands.value[currentCommandIndex.value].executed = true;
      commands.value[currentCommandIndex.value].progress = 100; // 设置为100%
    }
    
    // 停止进度动画
    stopProgressAnimation();
    
    // 不需要立即执行下一条命令，watch最终值变化时会触发下一条
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
    isExecuting.value = false;
    executionQueue.value = []; // 清空队列
    stopProgressAnimation(); // 停止进度动画
  }
};

const startProgressAnimation = (cmdIndex: number, duration: number) => {
  // 清除之前的进度动画
  stopProgressAnimation();
  
  // 重置进度
  if (cmdIndex >= 0 && cmdIndex < commands.value.length) {
    commands.value[cmdIndex].progress = 0;
  }
  
  // 计算更新间隔（基于持续时间）
  const totalSteps = 50; // 总更新次数
  const interval = (duration * 1000) / totalSteps;
  
  // 启动进度更新
  progressInterval.value = window.setInterval(() => {
    if (cmdIndex >= 0 && cmdIndex < commands.value.length) {
      const currentProgress = commands.value[cmdIndex].progress || 0;
      const newProgress = Math.min(currentProgress + (100 / totalSteps), 100);
      commands.value[cmdIndex].progress = newProgress;
      
      // 如果达到100%，停止动画
      if (newProgress >= 100) {
        stopProgressAnimation();
      }
    }
  }, interval);
};

const stopProgressAnimation = () => {
  if (progressInterval.value) {
    clearInterval(progressInterval.value);
    progressInterval.value = null;
  }
};

const resetExecution = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/commands/reset', {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('重置失败，请重试');
    }
    
    finalValue.value = 0;
    displayValue.value = 0;
    executionHistory.value = [];
    executionQueue.value = [];
    currentCommandIndex.value = -1;
    
    // 重置所有命令状态
    commands.value.forEach(cmd => {
      cmd.executed = false;
      cmd.progress = 0;
    });
    
    // 停止动画
    stopProgressAnimation();
    
    // 停止状态检查
    if (statusCheckInterval.value) {
      clearInterval(statusCheckInterval.value);
      statusCheckInterval.value = null;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
  }
};

// 组件加载时初始化
onMounted(() => {
  // 初始化显示值
  displayValue.value = finalValue.value;
});

// 组件卸载时清理定时器
onUnmounted(() => {
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value);
    statusCheckInterval.value = null;
  }
  
  stopProgressAnimation();
});
</script>

<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧面板：当前数值和控制按钮 -->
        <div class="lg:col-span-1">
          <div class="flex flex-col h-full">
            <!-- 实时数值显示 -->
            <div class="mb-6">
              <ValueDisplay :value="displayValue" />
            </div>
            
            <!-- 控制面板 -->
            <ControlPanel
              :isExecuting="isExecuting"
              :error="error"
              @execute="executeCommands"
              @reset="resetExecution"
            />
          </div>
        </div>
        
        <!-- 右侧面板：命令列表和执行历史 -->
        <div class="lg:col-span-2">
          <!-- 命令列表 -->
          <div class="mb-6">
            <CommandList 
              :commands="commands" 
              :currentCommandIndex="currentCommandIndex" 
            />
          </div>
          
          <!-- 执行历史 -->
          <ExecutionHistory :history="executionHistory" />
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
}
</style> 
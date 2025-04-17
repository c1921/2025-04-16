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

// 从后端获取命令列表，而不是在前端定义
const commands = ref<Command[]>([]);

const finalValue = ref<number>(0);
const displayValue = ref<number>(0);
const executionHistory = ref<ExecutionHistory[]>([]);
const isExecuting = ref<boolean>(false);
const error = ref<string | null>(null);
const statusCheckInterval = ref<number | null>(null);
const currentCommandIndex = ref<number>(-1);
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
    }
  };
  
  requestAnimationFrame(animate);
});

// 从后端获取所有命令
const fetchCommands = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/commands');
    if (response.ok) {
      const data = await response.json();
      commands.value = data;
    } else {
      error.value = '获取命令列表失败';
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取命令列表失败';
  }
};

const executeCommands = async () => {
  try {
    isExecuting.value = true;
    error.value = null;
    
    // 清空历史记录
    executionHistory.value = [];
    currentCommandIndex.value = -1;
    
    // 初始化执行流程
    const response = await fetch('http://localhost:8000/api/commands/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error('执行命令失败，请重试');
    }
    
    const data = await response.json();
    finalValue.value = data.final_value;
    
    // 更新命令列表状态
    if (data.commands) {
      commands.value = data.commands;
    }
    
    // 开始逐条执行命令
    executeNextCommand();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
    isExecuting.value = false;
  }
};

const executeNextCommand = async () => {
  try {
    // 查找当前正在执行的命令
    const currentCmd = commands.value.find(cmd => !cmd.executed);
    if (currentCmd) {
      currentCommandIndex.value = commands.value.findIndex(cmd => cmd.id === currentCmd.id);
    } else {
      isExecuting.value = false;
      return;
    }
    
    // 开始进度条动画
    if (currentCommandIndex.value >= 0) {
      startProgressAnimation(currentCommandIndex.value, commands.value[currentCommandIndex.value].duration);
    }
    
    // 调用API执行下一条命令
    const response = await fetch('http://localhost:8000/api/commands/execute-next', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error('执行命令失败，请重试');
    }
    
    const data = await response.json();
    
    if (data.status === 'no_execution' || data.error) {
      throw new Error(data.error || '没有正在进行的执行任务');
    }
    
    finalValue.value = data.final_value;
    
    // 添加到执行历史
    if (data.execution) {
      executionHistory.value.push(data.execution);
    }
    
    // 更新命令状态
    if (data.command) {
      const cmdIndex = commands.value.findIndex(c => c.id === data.command.id);
      if (cmdIndex >= 0) {
        commands.value[cmdIndex].executed = true;
        commands.value[cmdIndex].progress = 100;
      }
    }
    
    // 停止进度动画
    stopProgressAnimation();
    
    // 如果还有未执行的命令，继续执行
    if (data.status === 'in_progress' && data.remaining_commands > 0) {
      // 延迟一段时间后执行下一条命令，让用户能看到当前命令已完成
      setTimeout(() => {
        executeNextCommand();
      }, 800);
    } else {
      isExecuting.value = false;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发生未知错误';
    isExecuting.value = false;
    stopProgressAnimation();
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
    currentCommandIndex.value = -1;
    
    // 重新获取命令列表（重置状态）
    await fetchCommands();
    
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
onMounted(async () => {
  // 获取命令列表
  await fetchCommands();
  
  // 获取最新状态
  fetchCurrentStatus();
});

// 获取当前状态
const fetchCurrentStatus = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/commands/status');
    if (response.ok) {
      const data = await response.json();
      if (data.status !== 'no_execution' && data.final_value !== undefined) {
        finalValue.value = data.final_value;
        displayValue.value = data.final_value;
        
        // 更新执行历史
        if (data.execution_history) {
          executionHistory.value = data.execution_history;
        }
        
        // 更新命令状态
        if (data.commands) {
          data.commands.forEach((cmd: Command) => {
            const index = commands.value.findIndex(c => c.id === cmd.id);
            if (index >= 0) {
              commands.value[index].executed = cmd.executed;
              commands.value[index].progress = cmd.executed ? 100 : 0;
            }
          });
        }
      }
    }
  } catch (err) {
    console.error('获取状态失败:', err);
    // 不显示错误，静默处理
  }
};

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
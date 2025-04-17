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

// 添加一个新的ref用于控制是否自动循环
const autoRestart = ref<boolean>(true);

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
    
    // 先停止所有进度动画
    stopProgressAnimation();
    
    // 重置命令的执行状态和进度
    commands.value.forEach(cmd => {
      cmd.executed = false;
      cmd.progress = 0;
    });
    
    currentCommandIndex.value = -1;
    
    // 初始化执行流程，传递当前的finalValue
    const response = await fetch('http://localhost:8000/api/commands/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        initial_value: finalValue.value
      })
    });
    
    if (!response.ok) {
      throw new Error('执行命令失败，请重试');
    }
    
    const data = await response.json();
    
    // 更新命令列表状态，确保所有进度都为0
    if (data.commands) {
      commands.value = data.commands.map((cmd: Command) => ({
        ...cmd,
        executed: false,
        progress: 0
      }));
    }
    
    // 添加短暂延迟，确保UI更新完成后再开始执行
    setTimeout(() => {
      executeNextCommand();
    }, 50);
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
    
    // 更新命令状态，确保进度为100%
    if (data.command) {
      const cmdIndex = commands.value.findIndex(c => c.id === data.command.id);
      if (cmdIndex >= 0) {
        // 停止进度动画
        stopProgressAnimation();
        
        // 设置命令为已执行状态，进度为100%
        commands.value[cmdIndex].executed = true;
        commands.value[cmdIndex].progress = 100;
      }
    }
    
    // 如果还有未执行的命令，继续执行
    if (data.status === 'in_progress' && data.remaining_commands > 0) {
      // 延迟一段时间后执行下一条命令，让用户能看到当前命令已完成
      setTimeout(() => {
        executeNextCommand();
      }, 800);
    } else {
      // 所有命令执行完毕
      if (autoRestart.value) {
        // 如果启用了自动重启，延迟一段时间后开始新的循环
        setTimeout(() => {
          executeCommands();
        }, 1500);
      } else {
        isExecuting.value = false;
      }
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
  
  // 确保所有命令的进度状态正确
  commands.value.forEach((cmd, index) => {
    if (index !== cmdIndex && !cmd.executed) {
      cmd.progress = 0;
    } else if (cmd.executed) {
      cmd.progress = 100;
    }
  });
  
  // 重置当前命令的进度
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
      const newProgress = Math.min(currentProgress + (100 / totalSteps), 99); // 最多到99%，等待后端确认完成
      commands.value[cmdIndex].progress = newProgress;
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
    // 停止自动循环
    autoRestart.value = false;
    isExecuting.value = false;
    error.value = null;
    
    // 重置命令状态和执行历史
    executionHistory.value = [];
    finalValue.value = 0;
    displayValue.value = 0;
    currentCommandIndex.value = -1;
    
    // 重置命令状态
    commands.value.forEach(cmd => {
      cmd.executed = false;
      cmd.progress = 0;
    });
    
    // 调用后端重置API
    const response = await fetch('http://localhost:8000/api/commands/reset', {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('重置失败，请重试');
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '重置失败';
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

// 添加一个方法来停止自动循环
const stopExecution = () => {
  autoRestart.value = false;
  isExecuting.value = false;
};
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
    <!-- 左侧控制面板和状态 -->
    <div class="md:col-span-2">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body p-3">
          
          <div class="my-2">
            <ValueDisplay :value="displayValue" />
          </div>
          
          <div class="flex items-center my-1">
            <div class="form-control">
              <label class="label cursor-pointer py-1">
                <span class="label-text mr-2">自动循环</span>
                <input type="checkbox" v-model="autoRestart" class="toggle toggle-primary toggle-sm" />
              </label>
            </div>
          </div>
          
          <ControlPanel 
            :is-executing="isExecuting" 
            :error="error"
            @start="executeCommands" 
            @stop="stopExecution" 
            @reset="resetExecution"
          />
        </div>
      </div>
    </div>

    <!-- 右侧命令列表和执行历史 -->
    <div class="md:col-span-3">
      <!-- 命令列表 -->
      <div class="card bg-base-100 shadow-xl mb-3">
        <div class="card-body p-3">
          <h2 class="card-title text-lg mb-1">命令列表</h2>
          <CommandList 
            :commands="commands" 
            :current-command-index="currentCommandIndex"
          />
        </div>
      </div>
      
      <!-- 执行历史 -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body p-3">
          <h2 class="card-title text-lg mb-1">执行历史</h2>
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
:deep(.btn) {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  height: auto;
  min-height: 2.5rem;
}
:deep(.card-title) {
  margin-bottom: 0.25rem;
}
</style>
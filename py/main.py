from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
import random
from typing import List, Optional
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("app")

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许前端的来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Command(BaseModel):
    id: str
    name: str
    duration: float
    effect: float
    executed: bool = False
    progress: Optional[float] = 0

class CommandExecution(BaseModel):
    commands: List[Command] = []
    final_value: float = 0
    execution_history: List[dict] = []

class ExecuteRequest(BaseModel):
    """用于请求执行命令的模型"""
    commands: Optional[List[Command]] = None
    initial_value: float = 0.0

# 存储当前执行状态
current_execution: Optional[CommandExecution] = None

# 预定义的命令列表
predefined_commands = [
    Command(id="1", name="命令A", duration=1, effect=2, executed=False, progress=0),
    Command(id="2", name="命令B", duration=2, effect=-1, executed=False, progress=0),
    Command(id="3", name="命令C", duration=1.5, effect=3, executed=False, progress=0),
    Command(id="4", name="命令D", duration=0.5, effect=1, executed=False, progress=0),
]

# 请求记录中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应时间
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    
    return response

@app.get("/api/commands")
async def get_commands():
    """获取预定义的命令列表"""
    return predefined_commands

@app.post("/api/commands/execute")
async def execute_commands(request: ExecuteRequest = Body(...)):
    global current_execution
    
    # 获取初始值，默认为0
    initial_value = request.initial_value
    
    # 如果没有提供命令，使用预定义的命令列表
    commands = request.commands
    if commands is None or len(commands) == 0:
        commands = [Command(**cmd.dict()) for cmd in predefined_commands]
    
    # 重置执行状态，但保留初始值
    current_execution = CommandExecution(
        commands=commands,
        final_value=initial_value,
        execution_history=[]
    )
    
    # 随机打乱命令顺序
    random.shuffle(current_execution.commands)
    
    # 返回初始状态和待执行的命令列表
    return {
        "final_value": current_execution.final_value,
        "commands": current_execution.commands,
        "status": "ready",
        "remaining_commands": len(current_execution.commands)
    }

@app.post("/api/commands/execute-next")
async def execute_next_command():
    global current_execution
    
    if current_execution is None:
        return {"status": "no_execution", "error": "没有正在进行的执行任务"}
    
    # 查找下一个未执行的命令
    next_command = None
    for cmd in current_execution.commands:
        if not cmd.executed:
            next_command = cmd
            break
    
    if next_command is None:
        return {"status": "completed", "final_value": current_execution.final_value}
    
    # 模拟执行时间
    time.sleep(next_command.duration)
    
    # 更新最终值
    current_execution.final_value += next_command.effect
    
    # 准备执行历史记录
    execution_record = {
        "command_id": next_command.id,
        "command_name": next_command.name,
        "effect": next_command.effect,
        "current_value": current_execution.final_value,
        "timestamp": time.time()
    }
    
    # 记录执行历史
    current_execution.execution_history.append(execution_record)
    
    # 标记命令已执行
    next_command.executed = True
    next_command.progress = 100
    
    # 计算剩余未执行命令数量
    remaining_commands = sum(1 for cmd in current_execution.commands if not cmd.executed)
    
    # 返回执行结果
    return {
        "command": next_command,
        "final_value": current_execution.final_value,
        "execution": execution_record,
        "status": "in_progress" if remaining_commands > 0 else "completed",
        "remaining_commands": remaining_commands
    }

@app.post("/api/commands/execute-one")
async def execute_one_command(command: Command):
    global current_execution
    
    # 初始化执行状态（如果是第一次执行）
    if current_execution is None:
        current_execution = CommandExecution(
            commands=[],
            final_value=0,
            execution_history=[]
        )
    
    logger.info(f"执行单个命令: {command.name}, 效果: {command.effect}")
    
    # 模拟执行时间
    time.sleep(command.duration)
    
    # 更新最终值
    current_execution.final_value += command.effect
    
    # 准备执行历史记录
    execution_record = {
        "command_id": command.id,
        "command_name": command.name,
        "effect": command.effect,
        "current_value": current_execution.final_value,
        "timestamp": time.time()
    }
    
    # 记录执行历史
    current_execution.execution_history.append(execution_record)
    
    # 标记命令已执行
    command.executed = True
    command.progress = 100
    
    # 将命令添加到已执行的命令列表
    current_execution.commands.append(command)
    
    # 返回执行结果
    return {
        "final_value": current_execution.final_value,
        "execution": execution_record
    }

@app.get("/api/commands/status")
async def get_execution_status():
    if current_execution is None:
        return {"status": "no_execution"}
    return current_execution

@app.post("/api/commands/reset")
async def reset_execution():
    global current_execution
    
    # 重置执行状态
    current_execution = None
    
    # 返回成功消息
    return {"status": "reset", "message": "执行状态已重置"}

@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok", "timestamp": time.time()}

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from fastapi import FastAPI, Request
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

class CommandExecution(BaseModel):
    commands: List[Command] = []
    final_value: float = 0
    execution_history: List[dict] = []

# 存储当前执行状态
current_execution: Optional[CommandExecution] = None

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

@app.post("/api/commands/execute")
async def execute_commands(commands: List[Command]):
    global current_execution
    
    # 重置执行状态
    current_execution = CommandExecution(
        commands=commands,
        final_value=0,
        execution_history=[]
    )
    
    # 随机打乱命令顺序
    random.shuffle(current_execution.commands)
    
    # 依次执行命令
    for cmd in current_execution.commands:
        # 模拟执行时间
        time.sleep(cmd.duration)
        
        # 更新最终值
        current_execution.final_value += cmd.effect
        
        # 记录执行历史
        current_execution.execution_history.append({
            "command_id": cmd.id,
            "command_name": cmd.name,
            "effect": cmd.effect,
            "current_value": current_execution.final_value,
            "timestamp": time.time()
        })
        
        # 标记命令已执行
        cmd.executed = True
    
    return current_execution

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
    current_execution = None
    logger.info("重置命令执行状态")
    return {"status": "reset"}

@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok", "timestamp": time.time()}

if __name__ == "__main__":
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000) 
"""
FastAPI server for Motorcycle AR Coach environment
"""

import sys
import os
from pathlib import Path

# Add the server directory to Python path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid

# Now import from the same directory
from motorcycle_env import MotorcycleEnvironment
from models import MotorcycleAction, MotorcycleObservation

app = FastAPI(title="Motorcycle AR Coach Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active environments
sessions: Dict[str, MotorcycleEnvironment] = {}

class ResetResponse(BaseModel):
    session_id: str
    observation: MotorcycleObservation

class StepResponse(BaseModel):
    observation: MotorcycleObservation
    reward: float
    done: bool
    info: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Motorcycle AR Coach Environment", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/reset", response_model=ResetResponse)
async def reset_environment(task: str = "cornering"):
    """Reset the environment with a specific task"""
    session_id = str(uuid.uuid4())
    env = MotorcycleEnvironment(task=task)
    sessions[session_id] = env
    obs = env.reset()
    return ResetResponse(session_id=session_id, observation=obs)

@app.post("/step", response_model=StepResponse)
async def step_environment(session_id: str, action: MotorcycleAction):
    """Take a step in the environment"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = sessions[session_id]
    obs, reward, done, info = env.step(action)
    
    if done:
        # Clean up session
        del sessions[session_id]
    
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/task_score/{session_id}/{task_name}")
async def get_task_score(session_id: str, task_name: str):
    """Get grader score for a specific task"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = sessions[session_id]
    score = env.get_task_score(task_name)
    return {"task": task_name, "score": score}
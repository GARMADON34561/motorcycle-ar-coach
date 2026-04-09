"""
FastAPI server for Motorcycle AR Coach environment
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

print("=== Starting Motorcycle AR Coach Server ===")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")
print(f"Files in server directory: {os.listdir('server') if os.path.exists('server') else 'server folder not found'}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid

# Try to import
try:
    print("Attempting to import from motorcycle_env...")
    from server.motorcycle_env import MotorcycleEnvironment
    print("✓ Import successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    traceback.print_exc()
    raise

try:
    print("Attempting to import models...")
    from server.models import MotorcycleAction, MotorcycleObservation
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Models import failed: {e}")
    traceback.print_exc()
    raise

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

class StepRequest(BaseModel):
    session_id: str
    action: MotorcycleAction

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

@app.post("/reset")
async def reset_environment(task: str = "cornering"):
    """Reset the environment with a specific task"""
    try:
        print(f"=== RESET CALLED ===")
        print(f"Task: {task}")
        
        # Test 1: Create environment
        print("Creating MotorcycleEnvironment...")
        env = MotorcycleEnvironment(task=task)
        print("✓ Environment created")
        
        # Test 2: Reset
        print("Calling reset()...")
        obs = env.reset()
        print(f"✓ Reset successful, speed: {obs.speed}")
        
        # Test 3: Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = env
        print(f"✓ Session created: {session_id[:8]}")
        
        # Test 4: Return response
        response = {"session_id": session_id, "observation": obs.dict()}
        print("Returning response")
        return response
        
    except Exception as e:
        print(f"✗ RESET ERROR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/step")
async def step_environment(request: StepRequest):
    """Take a step in the environment"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = sessions[request.session_id]
    obs, reward, done, info = env.step(request.action)
    
    if done:
        del sessions[request.session_id]
    
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/task_score/{session_id}/{task_name}")
async def get_task_score(session_id: str, task_name: str):
    """Get grader score for a specific task"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    env = sessions[session_id]
    score = env.get_task_score(task_name)
    return {"task": task_name, "score": score}
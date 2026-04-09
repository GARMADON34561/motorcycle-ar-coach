"""
FastAPI server for Motorcycle AR Coach environment
"""

import sys
import os
import traceback
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())

print("=== Starting Motorcycle AR Coach Server ===")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any

# Import
try:
    from server.motorcycle_env import MotorcycleEnvironment
    from server.models import MotorcycleAction, MotorcycleObservation
    print("✓ Imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    traceback.print_exc()
    raise

# Create FastAPI app FIRST
app = FastAPI(title="Motorcycle AR Coach Environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, MotorcycleEnvironment] = {}

class ResetResponse(BaseModel):
    session_id: str
    observation: MotorcycleObservation

class StepRequest(BaseModel):
    session_id: str
    action: MotorcycleAction

# THEN define all routes
@app.get("/")
async def root():
    return {"message": "Motorcycle AR Coach Environment", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test_env")
async def test_env():
    """Test endpoint to debug environment creation"""
    try:
        env = MotorcycleEnvironment(task="cornering")
        obs = env.reset()
        return {"success": True, "speed": obs.speed, "rpm": obs.rpm}
    except Exception as e:
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}

@app.post("/reset")
async def reset_environment(task: str = "cornering"):
    """Reset the environment with a specific task"""
    try:
        print(f"=== RESET CALLED ===")
        print(f"Task parameter: {task}")
        
        # Validate task
        if task not in ["cornering", "emergency", "efficiency"]:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid task: {task}. Must be one of: cornering, emergency, efficiency"}
            )
        
        session_id = str(uuid.uuid4())
        print(f"Creating environment for task: {task}")
        env = MotorcycleEnvironment(task=task)
        
        print("Resetting environment...")
        obs = env.reset()
        
        print(f"Storing session: {session_id[:8]}")
        sessions[session_id] = env
        
        print("Returning response")
        return {"session_id": session_id, "observation": obs.dict()}
        
    except Exception as e:
        print(f"✗ RESET ERROR: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

@app.post("/step")
async def step_environment(request: StepRequest):
    """Take a step in the environment"""
    if request.session_id not in sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    try:
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
    except Exception as e:
        print(f"Step error: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/task_score/{session_id}/{task_name}")
async def get_task_score(session_id: str, task_name: str):
    """Get grader score for a specific task"""
    if session_id not in sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    try:
        env = sessions[session_id]
        score = env.get_task_score(task_name)
        return {"task": task_name, "score": score}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
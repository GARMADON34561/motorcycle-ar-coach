@app.post("/reset")
async def reset_environment():
    """Reset the environment with default task"""
    try:
        print("Reset called")
        session_id = str(uuid.uuid4())
        env = MotorcycleEnvironment(task="cornering")
        obs = env.reset()
        sessions[session_id] = env
        print(f"Reset success, session: {session_id[:8]}")
        return {"session_id": session_id, "observation": obs.dict()}
    except Exception as e:
        print(f"Reset error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
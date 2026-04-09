from pydantic import BaseModel 
 
class MotorcycleAction(BaseModel): 
    """Actions the AI can take""" 
    throttle_delta: float = 0.0  # -0.1 to 0.1 
    brake_pressure: float = 0.0  # 0 to 1 
    lean_angle_delta: float = 0.0  # -5 to 5 degrees 
    gear_up: bool = False 
    gear_down: bool = False 
 
class MotorcycleObservation(BaseModel): 
    """What the AI sees from the environment""" 
    speed: float  # km/h 
    rpm: int  # engine speed 
    gear: int  # 1-6 
    lean_angle: float  # degrees 
    distance_to_obstacle: float  # meters, infinity if none 
    fuel_used: float  # liters 
    distance: float  # km traveled 
    is_crashed: bool 

import random
import math
from typing import Tuple, Dict, Any
from models import MotorcycleAction, MotorcycleObservation

class MotorcycleEnvironment:
    """AR Motorcycle Coach Environment - 3 tasks for RL training"""
    
    def __init__(self, task: str = "cornering"):
        """Initialize with one of three tasks: cornering, emergency, or efficiency"""
        self.task = task
        self.reset()
    
    def reset(self) -> MotorcycleObservation:
        """Reset the environment to start a new episode"""
        self.speed = 40.0
        self.rpm = 3000
        self.gear = 3
        self.lean_angle = 0.0
        self.fuel_used = 0.0
        self.distance = 0.0
        self.is_crashed = False
        self.steps = 0
        self.max_steps = 200
        self.throttle = 0.5
        self.distance_to_obstacle = 50.0 if self.task == "emergency" else float('inf')
        return self._get_observation()
    
    def step(self, action: MotorcycleAction) -> Tuple[MotorcycleObservation, float, bool, Dict]:
        """Execute one action and return observation, reward, done, info"""
        if self.is_crashed:
            return self._get_observation(), -1.0, True, {}
        
        # Apply throttle (0-100% range)
        throttle = max(0, min(1, self.throttle + action.throttle_delta))
        self.throttle = throttle
        
        # Apply brake
        brake = action.brake_pressure
        
        # Apply lean angle change
        self.lean_angle += action.lean_angle_delta
        self.lean_angle = max(-45, min(45, self.lean_angle))
        
        # Gear changes
        if action.gear_up and self.gear < 6:
            self.gear += 1
        if action.gear_down and self.gear > 1:
            self.gear -= 1
        
        # Physics update
        acceleration = (throttle * 80) - (brake * 120) - (self.speed * 0.05)
        self.speed += acceleration * 0.1
        self.speed = max(0, min(180, self.speed))
        
        # RPM calculation
        self.rpm = int(self.speed / (self.gear * 0.02)) if self.speed > 0 else 1000
        self.rpm = max(800, min(11000, self.rpm))
        
        # Fuel consumption
        fuel_rate = throttle * (self.rpm / 1000) * 0.0005
        self.fuel_used += fuel_rate
        
        # Distance traveled
        self.distance += (self.speed / 3600) * 0.1
        
        # Obstacle update for emergency task
        if self.task == "emergency" and self.distance_to_obstacle < float('inf'):
            self.distance_to_obstacle -= (self.speed / 3600) * 0.1 * 1000
        
        # Crash detection (excessive lean or obstacle hit)
        if abs(self.lean_angle) > 40:
            self.is_crashed = True
        if self.task == "emergency" and self.distance_to_obstacle < 0:
            self.is_crashed = True
        
        self.steps += 1
        done = self.is_crashed or self.steps >= self.max_steps
        
        # Calculate reward based on task
        reward = self._calculate_reward()
        
        info = {"task": self.task, "steps": self.steps}
        return self._get_observation(), reward, done, info
    
    def _calculate_reward(self) -> float:
        """Calculate reward based on current task"""
        if self.is_crashed:
            return -1.0
        
        if self.task == "cornering":
            # Reward for smooth cornering at target speed
            target_speed = 40.0
            speed_penalty = abs(self.speed - target_speed) / target_speed
            lean_penalty = abs(self.lean_angle) / 45.0
            return max(0.1, 1.0 - (speed_penalty * 0.5 + lean_penalty * 0.5))
        
        elif self.task == "emergency":
            # Reward for avoiding obstacle
            if self.distance_to_obstacle < 0:
                return 0.0
            avoidance_bonus = 1.0 - min(1.0, self.distance_to_obstacle / 20.0)
            return max(0.1, avoidance_bonus)
        
        else:  # efficiency task
            # Reward for fuel efficiency while maintaining speed
            target_speed = 80.0
            speed_penalty = abs(self.speed - target_speed) / target_speed
            fuel_penalty = self.fuel_used / 0.5
            return max(0.1, 1.0 - (speed_penalty * 0.3 + fuel_penalty * 0.7))
    
    def _get_observation(self) -> MotorcycleObservation:
        """Return current observation"""
        return MotorcycleObservation(
            speed=self.speed,
            rpm=self.rpm,
            gear=self.gear,
            lean_angle=self.lean_angle,
            distance_to_obstacle=self.distance_to_obstacle if hasattr(self, 'distance_to_obstacle') else float('inf'),
            fuel_used=self.fuel_used,
            distance=self.distance,
            is_crashed=self.is_crashed
        )
    
    def get_task_score(self, task_name: str) -> float:
        """Return grader score for a specific task (0.0-1.0 exclusive)"""
        if task_name == "cornering":
            score = 0.7 - (abs(self.lean_angle) / 100)
        elif task_name == "emergency":
            score = 0.8 if not self.is_crashed and self.steps > 50 else 0.3
        elif task_name == "efficiency":
            fuel_per_km = self.fuel_used / (self.distance + 0.001)
            score = max(0.1, min(0.99, 1.0 - (fuel_per_km / 0.1)))
        else:
            score = 0.5
        return max(0.05, min(0.95, score))
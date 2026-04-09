---
title: Motorcycle AR Coach
emoji: 🏍️
colorFrom: gray
colorTo: pink
sdk: docker
pinned: false
---

# Motorcycle AR Coach Environment

An OpenEnv RL environment for training AI agents to ride motorcycles safely and efficiently, designed for AR glasses integration.

## Real-World Utility

This environment simulates real motorcycle riding scenarios that Meta Glasses could assist with:
- **Cornering assistance** - Real-time lean angle coaching
- **Emergency avoidance** - Hazard detection and response
- **Fuel efficiency** - Eco-riding optimization

## Three Tasks with Graders

| Task | Difficulty | Grader Range | Description |
|------|------------|--------------|-------------|
| Cornering | Easy | 0.1-0.9 | Smooth 90° turn at 40 km/h |
| Emergency | Medium | 0.1-0.9 | Obstacle avoidance with braking |
| Efficiency | Hard | 0.1-0.9 | 5km fuel-minimization course |

## Action Space

- `throttle_delta`: float (-0.1 to 0.1)
- `brake_pressure`: float (0 to 1)
- `lean_angle_delta`: float (-5 to 5 degrees)
- `gear_up`: bool
- `gear_down`: bool

## Observation Space

- `speed`: km/h
- `rpm`: engine speed
- `gear`: 1-6
- `lean_angle`: degrees
- `distance_to_obstacle`: meters
- `fuel_used`: liters
- `distance`: km
- `is_crashed`: bool

## Setup

```bash
docker build -t motorcycle-ar-coach .
docker run -p 7860:7860 motorcycle-ar-coach
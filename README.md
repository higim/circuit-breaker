# Circuit Breaker Pattern — Async Python Implementation

A lightweight, production-ready **Circuit Breaker** decorator for Python async functions.  
It helps your system **fail fast**, **recover gracefully**, and **avoid cascading failures** when dependencies become unreliable.

---

## Features

- Works with **async functions** (`async def`)
- Configurable **max consecutive errors**
- Built-in **exponential backoff + jitter**
- Exposes **circuit state** (`OPEN` / `CLOSED`)
---

## What Is a Circuit Breaker?

In distributed systems, repeated retries against a failing dependency can overload the system and cause a full outage.

A **Circuit Breaker** detects repeated failures and "opens" the circuit to **block further calls** until recovery is possible.  
Once enough time has passed, it **tests** the connection again — closing the circuit on success.

**States:**
- `CLOSED`: normal operation  
- `OPEN`: failures exceeded threshold — requests blocked  
- `HALF-OPEN`: testing recovery  

---

## Example Usage

```python
from circuit_breaker import CircuitBreaker, OpenCircuitException
import random

breaker = CircuitBreaker(max_consecutive_errors=3)

@breaker
async def call_api():
    if random.random() < 0.7:
        raise ConnectionError("API down")
    return "Success!"

# Use in your async code
try:
    result = await call_api()
except OpenCircuitException:
    print("Circuit is open — skipping request")


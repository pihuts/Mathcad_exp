# Architecture Patterns

**Domain:** Mathcad Automation App (Python/COM/Web)
**Researched:** Jan 25, 2026

## Recommended Architecture

**Pattern:** Asynchronous Process-Based Engine (Sidecar Pattern)

To satisfy the constraints of a blocking, single-threaded COM interface while maintaining a responsive UI, we **must** decouple the execution environment from the request handling environment.

### High-Level Diagram

```mermaid
graph TD
    User[User / Browser] <-->|HTTP/WebSocket| WebServer[Web Server (FastAPI)]
    
    subgraph "Main Process"
        WebServer
        StateManager[State Manager]
        JobQueue[Job Queue (IPC)]
        ResultQueue[Result Queue (IPC)]
    end
    
    subgraph "Engine Process (Independent)"
        Worker[Worker Loop]
        COM[Mathcad COM Object]
    end
    
    StateManager -->|Put Job| JobQueue
    JobQueue -->|Get Job| Worker
    Worker -->|Call| COM
    COM -->|Result| Worker
    Worker -->|Put Result| ResultQueue
    ResultQueue -->|Consume| StateManager
    StateManager -->|Push Update| WebServer
```

### Component Boundaries

| Component | Responsibility | Communicates With | Isolation Strategy |
|-----------|---------------|-------------------|--------------------|
| **Web Server (API)** | Serves UI, accepts requests, manages connections (SSE/WS). | Client, State Manager | AsyncIO (Non-blocking) |
| **State Manager** | Tracks workflow state, manages Engine lifecycle (Start/Kill). | Web Server, Queues | In-memory / Database |
| **Job Queue** | Buffers requested calculations. | State Manager, Worker | `multiprocessing.Queue` |
| **Engine Worker** | Owns the COM instance. Executes blocking calls. | Queues, Mathcad App | **Separate Process** |

### Data Flow

1.  **Request:** User submits "Calculate Workflow" via Web UI.
2.  **Enqueue:** Web Server generates a Job ID and pushes payload to `JobQueue`. Returns "Accepted (202)" to UI.
3.  **Processing:** 
    *   Engine Process is idle -> picks up Job.
    *   Engine calls `mathcad.SetValue(...)`, `mathcad.Calculate()`, `mathcad.GetValue(...)`.
    *   **Crucial:** These calls block the Engine Process, but *not* the Web Server.
4.  **Completion:** Engine places results in `ResultQueue`.
5.  **Notification:** Web Server detects result, updates internal state, and pushes event via WebSocket to UI.

## Patterns to Follow

### Pattern 1: Process Isolation for COM (The "Airlock")
**What:** Run Mathcad interactions in a completely separate OS process, not just a thread.
**When:** Always, for COM automation of heavy desktop applications.
**Why:** 
1.  **Crash Safety:** If Mathcad segfaults or the COM bridge panics, it won't take down the Web Server.
2.  **Cancellation:** You cannot force-kill a Python thread safely. You *can* `terminate()` a process if Mathcad hangs or the user clicks "Stop".
3.  **GIL Avoidance:** Heavy data marshalling won't block web requests.

**Example (Conceptual):**
```python
# engine.py
import pythoncom
import win32com.client

def worker_main(queue_in, queue_out):
    # CRITICAL: Initialize COM in the worker process/thread
    pythoncom.CoInitialize() 
    mathcad = win32com.client.Dispatch("Mathcad.Application")
    
    while True:
        job = queue_in.get()
        if job == "STOP": break
        
        try:
            # Blocking call
            result = mathcad_calculate(mathcad, job)
            queue_out.put({"status": "success", "data": result})
        except Exception as e:
            queue_out.put({"status": "error", "msg": str(e)})
```

### Pattern 2: The "Poison Pill" & Watchdog
**What:** The State Manager monitors the Engine Process.
**When:** Handling the "Stop" button or timeouts.
**Mechanism:**
*   **Soft Stop:** Send a high-priority "STOP" message to the queue.
*   **Hard Stop:** If Engine doesn't respond in X seconds, call `process.terminate()`.
*   **Restart:** If the process dies unexpectedly (Mathcad crash), the State Manager automatically spawns a new one.

### Pattern 3: Snapshot-Based State Management
**What:** Treat the Mathcad worksheet as a pure function where possible.
**Why:** Mathcad is stateful. If Job A changes a variable, Job B sees that change.
**Mitigation:** 
*   **Reset Pattern:** Every job starts by ensuring the sheet is in a known state (or reloading the sheet).
*   **Input-Output Only:** Avoid relying on internal sheet state between HTTP requests.

## Anti-Patterns to Avoid

### Anti-Pattern 1: COM Object in Main Thread
**What:** Initializing `win32com.client.Dispatch` in the FastAPI/Flask startup event.
**Why bad:** The COM object belongs to the main thread. Any request trying to use it will block the *entire server*. Concurrent requests will timeout.
**Instead:** Pass *messages* to a worker, not *objects* to a thread.

### Anti-Pattern 2: Threading without CoInitialize
**What:** Spawning a `threading.Thread` and trying to use a global COM object.
**Why bad:** COM raises `CoInitialize has not been called` or random Access Violations.
**Instead:** Every thread/process must initialize its own COM context. Never share COM pointers across thread boundaries without explicit marshalling (which is fragile).

### Anti-Pattern 3: "Zombie" Mathcads
**What:** The Python script restarts, but leaves `Mathcad.exe` running in the background.
**Consequences:** Memory leaks, file locking conflicts (cannot open `.mcdx` because the previous invisible instance has it locked).
**Prevention:** 
*   Use `atexit` handlers to ensure `Application.Quit()` is called.
*   Check for and kill orphaned `Mathcad.exe` processes on startup (with user permission).

## Scalability Considerations

| Concern | Single User (Local) | Multi-User (Server) |
|---------|---------------------|---------------------|
| **Concurrency** | Queue length = 1. User waits for their own job. | Queue length = N. Users wait for *each other*. |
| **Licensing** | 1 License usually. | **Critical Bottleneck.** Mathcad is rarely licensed for server-side concurrent execution. |
| **Session Isolation** | Not needed. | **Hard.** Process A's variables overwrite Process B's. |

**Verdict:** This architecture assumes a **Single-User / Local Desktop** or **Single-Worker Server** model. True multi-user concurrency requires a pool of Worker Processes, each with a dedicated Mathcad instance (and license).

## Sources
- `pywin32` Documentation (COM Threading models)
- Microsoft COM STA (Single Threaded Apartment) specifications
- Standard "Job Queue" distributed system patterns

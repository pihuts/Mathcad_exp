# Feature Research

**Domain:** Mathcad Automation / Engineering Batch Calculation
**Researched:** Sun Jan 25 2026
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Excel Import/Export** | Engineers maintain load cases in Excel. Manual entry is a dealbreaker. | MEDIUM | Must handle sheets, headers, and type conversion. |
| **Alias Discovery** | Users expect the tool to "see" the Input/Output variables defined in Mathcad automatically. | MEDIUM | Relies on `InputRegion` and `OutputRegion` API. |
| **Series Generation** | Basic "Sweep parameter A from 1 to 10" is the core use case. | LOW | Linear (Start, End, Step) and List ([1, 5, 10]) modes. |
| **Continue-on-Error** | In a batch of 500, #43 *will* fail. The process must log it and move to #44. | HIGH | Requires robust try-catch around COM calls and process monitoring. |
| **Result Aggregation** | A single table view showing Input A | Input B | Result X | Result Y | Status. | MEDIUM | Data grid with sorting/filtering. |
| **Process Recycling** | Mathcad instances can leak memory or hang. Auto-restart after N runs is standard for stability. | HIGH | Watchdog process to kill/restart `mathcad.exe`. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Monte Carlo Inputs** | Allows probabilistic design (e.g., "Yield Strength = Normal(350, 20)"). | MEDIUM | Requires a random number generator with distribution support. |
| **Permutations (DOE)** | "Test every combination of these 3 lists" (Full Factorial). Automates the setup of massive grids. | LOW | Cartesian product generation logic. |
| **Parallel Execution** | Running 1000 cases sequentially is slow. Running 4 at once (on 4 cores) is 4x faster. | HIGH | **Technical Risk:** Does Mathcad API support concurrent instances? Needs feasibility study. |
| **Snapshot on Fail** | "Why did case #43 fail?" Save a copy of the `.mcdx` with inputs set to the failing state. | MEDIUM | SaveAs functionality triggered by error catch. |
| **Real-time Charting** | Visualizing convergence or trends *while* the batch runs (e.g., Scatter Plot of Output vs Input). | HIGH | Live updating charts. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **In-App Math Editing** | "Let me change the formula quickly here." | Replicates Mathcad's core (complex). Breaks "Source of Truth" (file vs app). | Open the file in Mathcad, edit, save, reload. |
| **Arbitrary Scripting** | "Let me write a loop in Python/C#." | High barrier to entry for non-coders. Security risks. Debugging nightmares. | Provide rich UI generators (Series, Random, Formula). |
| **Headless Only** | "Hide the window for speed." | Hard to debug if Mathcad pops up a dialog/error that the API misses. | "Minimized" mode or "Visible" toggle. |

## Feature Dependencies

```
[Alias Discovery]
    └──requires──> [Mathcad Installation]

[Excel Import]
    └──requires──> [Alias Discovery] (to map columns to vars)

[Monte Carlo Inputs]
    └──requires──> [Series Generation] (extends input logic)

[Parallel Execution]
    └──requires──> [Process Recycling] (management of multiple PIDs)
```

### Dependency Notes

- **Excel Import requires Alias Discovery:** You can't map Excel columns to Mathcad variables until you know what variables exist.
- **Parallel Execution requires Process Recycling:** Managing multiple concurrent COM instances is unstable; robust process lifecycle management is a prerequisite.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] **Alias Discovery** — Essential to connect the tool to the file.
- [ ] **Excel Import/Export** — The primary workflow integration.
- [ ] **Linear Series Generator** — The simplest internal input method.
- [ ] **Sequential Batch Runner** — Run 1..N, stop on finish.
- [ ] **Continue-on-Error** — Essential for usability (logs error, continues).
- [ ] **Result Grid** — View results.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Permutations (Full Factorial)** — High value for exploration.
- [ ] **Snapshot on Fail** — High value for debugging.
- [ ] **Process Recycling** — If stability proves to be an issue (likely).

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Parallel Execution** — High complexity, high risk.
- [ ] **Monte Carlo** — Niche use case compared to deterministic sweep.
- [ ] **Interactive Charts** — Nice, but Excel does this better for now.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| **Excel Import/Export** | HIGH | MEDIUM | P1 |
| **Alias Discovery** | HIGH | LOW | P1 |
| **Continue-on-Error** | HIGH | HIGH | P1 |
| **Result Grid** | HIGH | MEDIUM | P1 |
| **Permutations** | MEDIUM | LOW | P2 |
| **Snapshot on Fail** | HIGH | MEDIUM | P2 |
| **Parallel Execution** | HIGH | HIGH | P3 |
| **Monte Carlo** | MEDIUM | MEDIUM | P3 |
| **In-App Math Editing** | LOW | HIGH | SKIP |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Excel Data Tables | Custom Python Script | Our Approach |
|---------|-------------------|----------------------|--------------|
| **Setup** | Manual (Cell references) | High (Coding required) | **Auto-Discovery (Aliases)** |
| **Inputs** | Range/List only | Infinite (if you code it) | **Wizards (Excel, Range, Permutation)** |
| **Error Handling** | Stops/Breaks | Depends on coder skill | **Built-in "Continue & Log"** |
| **Speed** | Fast (Internal) | Variable | **Optimized Sequential (aiming for Parallel v2)** |
| **Visualization** | Excellent (Native Charts) | Library dependent (Matplotlib) | **Basic Grid + Export to Excel** |

## Sources

- **Competitor Analysis:** Excel Data Tables features (Microsoft).
- **Domain Knowledge:** Common requirements for FEA/CFD Parametric Studies (ANSYS/Abaqus workflows).
- **Constraint:** Mathcad Prime Automation API documentation (general knowledge of COM limitations).

# AVALYOS Python-Q# Integration Guide

## Overview

This project demonstrates complete integration between Python and Q# using the modern Azure Quantum QDK (`qsharp` package). Python code calls quantum operations and processes results.

---

## Project Structure

```
aval_program/
├── avalyos_quantum.qs              # Q# quantum operations
├── avalyos_quantum.csproj          # Q# project configuration
├── qsharp.json                     # Q# compilation settings
├── avalyos_python_qsharp.py        # Python-Q# integration layer
├── companies.json                  # AVALYOS dataset
└── avalyos.py                      # Standalone Python system
```

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
# Install Python qsharp package
pip install qsharp

# Verify installation
python -c "import qsharp; print('✓ qsharp installed')"
```

### Step 2: Verify Q# Project Structure

Ensure these files exist in your `aval_program` directory:

```bash
# Check Q# project files
ls -la *.csproj *.qs *.json
```

Should show:
- `avalyos_quantum.csproj` (Q# project)
- `avalyos_quantum.qs` (Q# operations)
- `qsharp.json` (Q# config)

### Step 3: Build Q# Project

```bash
# Navigate to project directory
cd c:\Users\USER\OneDrive\Desktop\aval_program

# Build the Q# project
dotnet build --project avalyos_quantum.csproj

# Expected output: "Build succeeded"
```

---

## Running the Integration

### Method 1: Run Python Integration Demo (Recommended)

```bash
cd c:\Users\USER\OneDrive\Desktop\aval_program
python avalyos_python_qsharp.py
```

**Expected Output:**
```
======================================================================
🌍 AVALYOS - Python & Quantum Integration Demo
======================================================================

🔧 Initializing quantum environment...
✓ Quantum environment initialized successfully!

======================================================================
DEMO 1: Single Quantum Sample
======================================================================

📊 QUANTUM-SAMPLED BRANCH DETAILS
======================================================================
Code:       pf01
Company:    Pfizer
Continent:  Asia
Country:    Singapore
State:      West
Sector:     Pharma
SubSector:  Pharmaceutical Manufacturing
Employees:  5500
======================================================================

[... continues with 10 samples and distribution analysis ...]
```

### Method 2: Run Standalone Q# Program

```bash
dotnet run --project avalyos_quantum.csproj
```

---

## How Python Ingests Q# Code

### The qsharp Package Architecture

```
Python Code
    ↓
qsharp.init()          ← Initializes Q# runtime
    ↓
qsharp.run()           ← Executes Q# operations
    ↓
Q# Compiled Code (.dll)
    ↓
Quantum Simulator / Azure Quantum
```

### Step-by-Step Execution Flow

1. **Import qsharp**
   ```python
   import qsharp
   ```

2. **Initialize Environment**
   ```python
   qsharp.init(project_root=".")
   ```
   - Discovers `.qs` files in project
   - Loads compiled Q# assemblies
   - Sets up quantum runtime

3. **Call Q# Operations**
   ```python
   result = qsharp.run("AVALYOS.Quantum.SampleBranchWeighted()")
   ```
   - Executes Q# operation by fully qualified name
   - Returns results as Python types
   - Handles quantum measurement automatically

---

## Code Examples

### Example 1: Single Quantum Sample

```python
import qsharp

# Initialize
qsharp.init(project_root=".")

# Call Q# operation
result = qsharp.run("AVALYOS.Quantum.SampleBranchWeighted()")

# Access results (returns dictionary-like object)
print(f"Company: {result['Company']}")
print(f"Employees: {result['Employees']}")
```

### Example 2: Multiple Samples with Loop

```python
# Sample 5 branches
samples = []
for i in range(5):
    branch = qsharp.run("AVALYOS.Quantum.SampleBranchWeighted()")
    samples.append(branch)
    print(f"Sample {i+1}: {branch['Company']}")
```

### Example 3: Calling with Arguments

```python
# If your Q# operation takes parameters:
# operation MyOp(param: Int) : String { ... }

result = qsharp.run("AVALYOS.Quantum.MyOp(10)")
print(result)
```

### Example 4: Getting Operation Metadata

```python
# Get information about available operations
operations = qsharp.get_available_operations()
for op in operations:
    print(f"Operation: {op}")
```

---

## Understanding qsharp.packages.add()

The `qsharp.packages.add()` method is used for **external packages only**:

```python
# For external Q# libraries (not needed for local projects)
qsharp.packages.add("Microsoft.Quantum.Chemistry")

# For your local project, use qsharp.init() instead
qsharp.init(project_root=".")
```

**You do NOT need** `qsharp.packages.add()` for:
- Local Q# files (.qs)
- Project-specific operations
- Your AVALYOS quantum code

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           Python (avalyos_python_qsharp.py)         │
│  ┌────────────────────────────────────────────────┐ │
│  │ Functions:                                     │ │
│  │  - init_quantum_environment()                  │ │
│  │  - sample_branch()                             │ │
│  │  - sample_branches_multiple()                  │ │
│  │  - analyze_sampling_distribution()             │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────┘
                       │ qsharp.init()
                       │ qsharp.run()
                       ↓
┌──────────────────────────────────────────────────────┐
│         qsharp Python Package (Runtime)              │
│  - Loads .qs files from project                      │
│  - Compiles Q# to IL                                 │
│  - Manages quantum simulator                         │
└──────────────────────┬───────────────────────────────┘
                       │
                       ↓
┌──────────────────────────────────────────────────────┐
│          Q# Code (avalyos_quantum.qs)                │
│  ┌────────────────────────────────────────────────┐  │
│  │ Namespace AVALYOS.Quantum:                     │  │
│  │  - Branch newtype                              │  │
│  │  - GetSampleBranches()                         │  │
│  │  - QuantumRandomInt()                          │  │
│  │  - SampleBranchWeighted()                      │  │
│  │  - RunTest() @EntryPoint                       │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │
                       ↓
         Quantum Simulator or Azure Quantum
```

---

## Troubleshooting

### Error: "qsharp module not found"

```bash
# Solution: Install qsharp
pip install qsharp --upgrade
```

### Error: "Could not find Q# project"

```bash
# Solution: Ensure you're in the correct directory
cd c:\Users\USER\OneDrive\Desktop\aval_program
ls qsharp.json avalyos_quantum.qs
```

### Error: "Operation not found"

```bash
# Solution: Verify operation name and namespace
# Should be: AVALYOS.Quantum.SampleBranchWeighted
# NOT: SampleBranchWeighted alone
```

### Error: "Qubit not in |0⟩ state"

```bash
# Solution: Ensure ResetAll(qubits) is called before qubit release
# This is already fixed in your code ✓
```

---

## Performance Notes

- **First run:** Takes ~2-5 seconds (initialization overhead)
- **Subsequent runs:** ~100-500ms per quantum operation
- **Multiple samples:** Scales linearly with number of calls

---

## Next Steps

1. ✅ Run `python avalyos_python_qsharp.py`
2. ✅ Observe quantum-sampled branches
3. ✅ Modify `sample_branches_multiple()` to change sample count
4. ✅ Add your own Python analysis functions
5. ✅ Integrate with Azure Quantum (future)

---

## Resources

- **qsharp package docs:** https://docs.microsoft.com/qsharp/
- **Azure Quantum:** https://azure.microsoft.com/quantum/
- **Q# Language reference:** https://docs.microsoft.com/qsharp/language/

---

**Last Updated:** November 25, 2025  
**Project:** AVALYOS - Company Structure Management System

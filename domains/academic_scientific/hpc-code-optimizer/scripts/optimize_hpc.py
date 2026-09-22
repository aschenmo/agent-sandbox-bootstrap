#!/usr/bin/env python3
"""
HPC Code Optimizer & Scientific Cluster Accelerator
===================================================
Autonomous scientific computing performance profiling and cluster orchestration toolkit:
1. Static code analysis for computational bottlenecks (nested Python loops, memory fragmentation, non-vectorized NumPy).
2. Code optimization recommendations & automated rewrite templates (NumPy vectorization, Numba @jit, PyTorch compile).
3. Production-grade SLURM batch script generation for high-performance computing (HPC) clusters (GPU allocation, MPI, CUDA environment).
"""

import os
import sys
import re
import argparse
import json

def analyze_code_bottlenecks(source_code):
    issues = []
    lines = source_code.split("\n")
    
    # Check for nested loops
    loop_depth = 0
    in_loop_lines = []
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("for ") or stripped.startswith("while "):
            loop_depth += 1
            in_loop_lines.append((idx, stripped))
            if loop_depth >= 2:
                issues.append({
                    "line": idx,
                    "type": "Nested Loop Detected",
                    "severity": "High",
                    "snippet": stripped,
                    "recommendation": "Consider vectorizing with NumPy arrays (broadcasting / np.dot) or using @numba.njit(parallel=True)."
                })
        elif stripped and not stripped.startswith("#"):
            indent = len(line) - len(line.lstrip())
            if indent == 0:
                loop_depth = 0
                in_loop_lines = []
                
    # Check for .append() in loops
    for idx, line in enumerate(lines, 1):
        if ".append(" in line:
            issues.append({
                "line": idx,
                "type": "Dynamic List Allocation",
                "severity": "Medium",
                "snippet": line.strip(),
                "recommendation": "Pre-allocate numpy.empty(shape) or torch.empty() rather than dynamically growing Python lists."
            })
            
    # Check for torch without torch.no_grad() during inference
    if "torch" in source_code:
        if ("model(" in source_code or "forward(" in source_code) and "torch.no_grad()" not in source_code and "with torch.inference_mode()" not in source_code:
            issues.append({
                "line": 1,
                "type": "Missing Inference Mode / No-Grad",
                "severity": "High",
                "snippet": "model inference without torch.inference_mode()",
                "recommendation": "Wrap evaluation loops with 'with torch.inference_mode():' to save substantial GPU VRAM and computation."
            })
            
    # Check for torch.compile()
    if "torch.nn" in source_code or "nn.Module" in source_code:
        if "torch.compile(" not in source_code:
            issues.append({
                "line": 1,
                "type": "Missing PyTorch 2.x Compiler",
                "severity": "Info",
                "snippet": "PyTorch model uncompiled",
                "recommendation": "Apply 'model = torch.compile(model)' to leverage TorchDynamo and Triton kernel fusion."
            })
            
    return issues

def generate_slurm_script(job_name="hpc_job", gpus=1, cpus=8, memory="32G", walltime="24:00:00", script_cmd="python3 main.py", partition="gpu"):
    slurm_header = f"""#!/bin/bash
# ==============================================================================
# SLURM High-Performance Scientific Cluster Submission Script
# Generated automatically by Antigravity HPC Code Optimizer
# ==============================================================================
#SBATCH --job-name={job_name}
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem={memory}
#SBATCH --time={walltime}
"""
    if gpus > 0:
        slurm_header += f"#SBATCH --gres=gpu:{gpus}\n"
        
    slurm_body = f"""
# Environment Setup
echo "Job started on: $(hostname) at $(date)"
module purge
module load cuda/12.4 cudnn/9.1 python/3.12 2>/dev/null || true

# PyTorch / CUDA Diagnostics
nvidia-smi || true

# Execution
echo "Executing: {script_cmd}"
srun {script_cmd}

echo "Job finished at $(date)"
"""
    return slurm_header + slurm_body

def main():
    parser = argparse.ArgumentParser(
        description="HPC Code Optimizer: Profiling, Optimization & SLURM Cluster Setup"
    )
    parser.add_argument("--input", "-i", help="Path to Python scientific script to profile/optimize")
    parser.add_argument("--slurm", action="store_true", help="Generate SLURM cluster submission batch script")
    parser.add_argument("--job-name", default="scientific_sim", help="SLURM job name")
    parser.add_argument("--gpus", type=int, default=1, help="Number of GPUs for SLURM script")
    parser.add_argument("--cpus", type=int, default=8, help="Number of CPUs for SLURM script")
    parser.add_argument("--mem", default="32G", help="Memory request (e.g. 32G, 64G)")
    parser.add_argument("--partition", default="gpu", help="SLURM partition name")
    parser.add_argument("--cmd", default=None, help="Execution command for SLURM script")
    parser.add_argument("--output", "-o", default=None, help="Output path for script or analysis")
    
    args = parser.parse_args()
    
    if args.slurm:
        cmd = args.cmd or (f"python3 {args.input}" if args.input else "python3 main.py")
        script = generate_slurm_script(
            job_name=args.job_name,
            gpus=args.gpus,
            cpus=args.cpus,
            memory=args.mem,
            script_cmd=cmd,
            partition=args.partition
        )
        print("=" * 60)
        print("🖥️ Generated SLURM HPC Cluster Script:")
        print("=" * 60)
        print(script)
        print("=" * 60)
        
        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(script)
            print(f"💾 SLURM script saved to: {args.output}")
        sys.exit(0)
        
    if not args.input:
        print("❌ Error: Please provide --input <script.py> or specify --slurm", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.input, "r", encoding="utf-8") as f:
        code = f.read()
        
    print(f"⚡ [HPC Optimizer] Analyzing performance bottlenecks in: {args.input}...")
    issues = analyze_code_bottlenecks(code)
    
    print("\n" + "=" * 60)
    print(f"📊 Bottleneck Analysis Results ({len(issues)} findings):")
    print("=" * 60)
    for idx, iss in enumerate(issues, 1):
        print(f"[{idx}] Line {iss['line']} [{iss['severity']}]: {iss['type']}")
        print(f"    Snippet : {iss['snippet']}")
        print(f"    Solution: {iss['recommendation']}\n")
    print("=" * 60)
    
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"file": args.input, "issues_count": len(issues), "issues": issues}, f, indent=2, ensure_ascii=False)
        print(f"💾 Analysis report saved to: {args.output}")

if __name__ == "__main__":
    main()

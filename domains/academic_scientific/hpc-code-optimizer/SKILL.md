---
name: hpc-code-optimizer
domain: academic_scientific
description: 科研高性能计算(HPC)与科学计算代码调优系统（静态性能瓶颈诊断、向量化与并行加速建议、SLURM集群作业调度批处理脚本自动生成）
dependencies: [numpy]
---

# 科研高性能计算与代码调优系统 (HPC Code Optimizer)

## 📌 核心定位与功能
面向大规模科学计算与机器学习模型训练，解决科研人员代码在超算集群运行效率低、GPU资源利用不充分以及 SLURM 调度配置繁琐问题：
1. **计算性能瓶颈静态诊断**：检测高耗时多重循环、动态列表分配、未开启 `torch.inference_mode()` 等常见低效模式。
2. **向量化与内核融合优化建议**：提供 NumPy 广播计算重构建议与 PyTorch 2.x `torch.compile` / Triton 加速指导。
3. **SLURM 超算批处理作业脚本生成**：针对集群环境，一键生成标准化 `#SBATCH` 作业调度脚本（节点、CPU、GPU、内存、CUDA/cuDNN 环境加载）。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill hpc-code-optimizer
```

### 2. 诊断科学计算脚本性能瓶颈
```bash
python3 optimize_hpc.py -i simulation.py -o /tmp/outputs/hpc_report.json
```

### 3. 一键生成 SLURM 超算作业调度脚本
```bash
python3 optimize_hpc.py --slurm --job-name "alphafold_batch" --gpus 2 --cpus 16 --mem "64G" --cmd "python3 run_simulation.py" -o /tmp/outputs/submit.slurm
```

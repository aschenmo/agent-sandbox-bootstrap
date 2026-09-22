---
name: gemini-multimodal-slicer
domain: deep_research
description: Google Gemini 风格长音视频多模态时序切片器（基于原生 ffmpeg 引擎，定时/场景关键帧抓取、音轨高保真切片与带精确时间戳的 index.json 多模态索引生成）
dependencies: []
---

# Google Gemini 风格长音视频多模态切片器 (Gemini Multimodal Slicer)

## 📌 核心定位与能力
面向学术讲座录屏、实验视频与长音频材料，结合 Google Gemini 原生超长多模态上下文特性，实现**音视频材料的精确时序切片与视觉接地 (Temporal Grounding)**：
1. **多模态时序抽帧**：按指定时间间隔（如每 2 秒、5 秒）批量抓取高清关键帧，自动格式化并归档为视觉资产。
2. **语音轨对齐分离**：抽取视频音轨并切分为固定秒数（如 10 秒、30 秒）的标准 16kHz 单声道 WAV 分段，便于语音识别与音频推理。
3. **时序索引总装 (Temporal Manifest)**：自动输出自包含的 `index.json`，为每一张图像和每一个音频片段打上毫秒级时序标签（`00:01:24.000`），无缝喂入大模型多模态提示词中。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill gemini-multimodal-slicer
```

### 2. 对长视频进行完整时序切片与多模态索引构建
```bash
python3 slice_media.py -i lecture.mp4 --interval 3 --audio-chunk 15 -o /tmp/outputs/lecture_slices/
```

### 3. 一键运行合成视频自检演示 (Demo 模式)
```bash
python3 slice_media.py --demo -o /tmp/outputs/demo_media_slices/
```

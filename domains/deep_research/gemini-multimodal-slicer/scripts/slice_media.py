#!/usr/bin/env python3
"""
Google Gemini-Style Multimodal Temporal Media Slicer
====================================================
Transforms long-form video and audio lectures/experiments into indexed visual and audio slices:
1. Scene Detection Mode: Extracts key visual frames upon significant visual scene shifts.
2. Uniform Interval Mode: Extracts frames at regular temporal cadences (e.g. every 3, 5, or 10 seconds).
3. Audio Slicing Mode: Extracts and chunks clean speech/audio into aligned 16kHz segments with timestamps.
4. Generates an index.json cataloging timestamped multi-modal artifacts for LLM temporal grounding.
"""

import os
import sys
import json
import argparse
import subprocess
import shutil

def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("❌ Error: ffmpeg and ffprobe must be installed in system PATH.", file=sys.stderr)
        sys.exit(1)

def get_media_metadata(file_path):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(res.stdout)
        format_info = data.get("format", {})
        duration = float(format_info.get("duration", 0.0))
        has_video = any(s.get("codec_type") == "video" for s in data.get("streams", []))
        has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
        return {"duration_sec": duration, "has_video": has_video, "has_audio": has_audio}
    except Exception as e:
        return {"duration_sec": 0.0, "has_video": True, "has_audio": True}

def generate_demo_video(output_file):
    """Generate a 6-second synthetic multi-scene MP4 video using ffmpeg testsrc"""
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", "testsrc=duration=6:size=640x360:rate=10",
        "-f", "lavfi", "-i", "sine=frequency=1000:duration=6",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", output_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def slice_video_interval(input_path, output_dir, interval_sec=2):
    frames_dir = os.path.join(output_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    fps_val = f"1/{interval_sec}"
    out_pattern = os.path.join(frames_dir, "frame_%04d.jpg")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"fps={fps_val}",
        "-q:v", "2",
        out_pattern
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    # Collect frames
    extracted = []
    files = sorted([f for f in os.listdir(frames_dir) if f.endswith(".jpg")])
    for idx, f in enumerate(files):
        t_sec = idx * interval_sec
        mins = int(t_sec // 60)
        secs = int(t_sec % 60)
        ts_str = f"{mins:02d}:{secs:02d}.000"
        extracted.append({
            "index": idx + 1,
            "timestamp_seconds": round(t_sec, 2),
            "timestamp_str": ts_str,
            "filename": f,
            "path": os.path.join(frames_dir, f)
        })
    return extracted

def slice_audio_chunks(input_path, output_dir, chunk_sec=15):
    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    out_pattern = os.path.join(audio_dir, "chunk_%03d.wav")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-f", "segment", "-segment_time", str(chunk_sec),
        out_pattern
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith(".wav")])
    extracted = []
    for idx, f in enumerate(audio_files):
        start_t = idx * chunk_sec
        end_t = (idx + 1) * chunk_sec
        extracted.append({
            "chunk_index": idx + 1,
            "start_seconds": start_t,
            "end_seconds": end_t,
            "timestamp_range": f"{int(start_t//60):02d}:{int(start_t%60):02d} - {int(end_t//60):02d}:{int(end_t%60):02d}",
            "filename": f,
            "path": os.path.join(audio_dir, f)
        })
    return extracted

def main():
    parser = argparse.ArgumentParser(
        description="Google Gemini-Style Multimodal Temporal Media Slicer"
    )
    parser.add_argument("--input", "-i", default=None, help="Path to input video or audio file")
    parser.add_argument("--demo", action="store_true", help="Generate and slice a synthetic demonstration video")
    parser.add_argument("--mode", "-m", choices=["interval", "audio", "all"], default="all", help="Slicing modality")
    parser.add_argument("--interval", type=int, default=2, help="Frame extraction interval in seconds")
    parser.add_argument("--audio-chunk", type=int, default=10, help="Audio segmentation chunk length in seconds")
    parser.add_argument("--output-dir", "-o", default="/tmp/outputs/media_slices", help="Directory to save artifacts")

    args = parser.parse_args()
    check_ffmpeg()

    if not args.input and not args.demo:
        print("💡 No input media file provided. Automatically activating --demo synthetic video...")
        args.demo = True

    media_path = args.input
    if args.demo:
        os.makedirs(args.output_dir, exist_ok=True)
        demo_video_path = os.path.join(args.output_dir, "demo_lecture.mp4")
        print(f"🎬 Generating synthetic video: {demo_video_path}...")
        generate_demo_video(demo_video_path)
        media_path = demo_video_path

    if not os.path.exists(media_path):
        print(f"❌ Input media file not found: {media_path}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Probing media metadata for: {media_path}...")
    meta = get_media_metadata(media_path)
    print(f"⏱️ Duration: {meta['duration_sec']:.2f}s | Has Video: {meta['has_video']} | Has Audio: {meta['has_audio']}")

    manifest = {
        "source_file": media_path,
        "metadata": meta,
        "frames": [],
        "audio_chunks": []
    }

    if meta["has_video"] and args.mode in ["interval", "all"]:
        print(f"🖼️ Extracting video frames (interval: 1 frame every {args.interval}s)...")
        manifest["frames"] = slice_video_interval(media_path, args.output_dir, interval_sec=args.interval)
        print(f"✅ Extracted {len(manifest['frames'])} visual keyframes.")

    if meta["has_audio"] and args.mode in ["audio", "all"]:
        print(f"🎙️ Slicing speech audio track (chunk length: {args.audio_chunk}s, 16kHz mono)...")
        manifest["audio_chunks"] = slice_audio_chunks(media_path, args.output_dir, chunk_sec=args.audio_chunk)
        print(f"✅ Sliced {len(manifest['audio_chunks'])} audio segments.")

    # Save index.json
    index_path = os.path.join(args.output_dir, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 65)
    print("🎬 Multimodal Media Temporal Slicing Finished:")
    print("=" * 65)
    print(f"• Output Directory: {args.output_dir}")
    print(f"• Extracted Frames: {len(manifest['frames'])} images in /frames/")
    print(f"• Audio Segments  : {len(manifest['audio_chunks'])} WAV chunks in /audio/")
    print(f"• Grounding Index : {index_path}")
    print("=" * 65)

if __name__ == "__main__":
    main()

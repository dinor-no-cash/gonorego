import sys
import os
import wave
import struct
import math
import subprocess
import shutil

def get_ffmpeg_bin():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    bin_path = shutil.which("ffmpeg")
    if bin_path:
        return bin_path
    return "ffmpeg"

def analyze_audio_volume_chunks(wav_path: str, chunk_duration: float = 0.12):
    """
    Reads WAV file and returns list of (is_talking, duration).
    """
    with wave.open(wav_path, 'r') as w:
        nchannels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        total_duration = nframes / float(framerate)
        
        frames_per_chunk = int(framerate * chunk_duration)
        chunks = []
        
        # Read entire audio
        raw_data = w.readframes(nframes)
        
    # Unpack samples
    if sampwidth == 2:
        fmt = f"<{nframes * nchannels}h"
        samples = struct.unpack(fmt, raw_data)
    else:
        # Fallback
        return [(True, chunk_duration)] * int(total_duration / chunk_duration)
        
    # If stereo, average channels
    if nchannels == 2:
        mono_samples = [(samples[i] + samples[i+1]) / 2.0 for i in range(0, len(samples), 2)]
    else:
        mono_samples = list(samples)
        
    # Calculate RMS for each chunk
    threshold = 500.0 # Silence threshold for 16-bit audio
    
    num_chunks = int(math.ceil(len(mono_samples) / frames_per_chunk))
    is_talking_list = []
    
    for i in range(num_chunks):
        chunk = mono_samples[i * frames_per_chunk : (i + 1) * frames_per_chunk]
        if not chunk:
            continue
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk))
        is_talking_list.append(rms > threshold)
        
    return is_talking_list, chunk_duration, total_duration

def build_concat_file(normal_img: str, open_img: str, wav_path: str, out_file: str):
    talking_chunks, chunk_dur, total_dur = analyze_audio_volume_chunks(wav_path, chunk_duration=0.12)
    
    normal_img_abs = os.path.abspath(normal_img).replace("\\", "/")
    open_img_abs = os.path.abspath(open_img).replace("\\", "/") if os.path.exists(open_img) else normal_img_abs
    
    lines = []
    current_time = 0.0
    
    # State tracking: toggle mouth open/close during talking
    mouth_open = False
    
    for is_talking in talking_chunks:
        if is_talking:
            # Toggle mouth for classic 2ch Flash animation chatter
            current_img = open_img_abs if mouth_open else normal_img_abs
            mouth_open = not mouth_open
        else:
            # Closed mouth during pauses / silence
            current_img = normal_img_abs
            mouth_open = False
            
        lines.append(f"file '{current_img}'")
        lines.append(f"duration {chunk_dur:.3f}")
        current_time += chunk_dur
        
    # End frame
    lines.append(f"file '{normal_img_abs}'")
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        
    print(f"=== Generated lipsync sequence -> {out_file} (Duration: {current_time:.2f}s) ===")

def render_video(wav_path: str, normal_img: str, open_img: str, out_mp4: str):
    concat_file = "frames.txt"
    build_concat_file(normal_img, open_img, wav_path, concat_file)

    ffmpeg_bin = get_ffmpeg_bin()
    print(f"Using ffmpeg at: {ffmpeg_bin}")

    cmd = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", wav_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", out_mp4
    ]
    print("Executing ffmpeg (Pure video + audio lipsync, NO subtitles):")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("ffmpeg video rendering failed!")
    print(f"=== Successfully rendered clean Flash video: {out_mp4} ===")

if __name__ == "__main__":
    wav = sys.argv[1] if len(sys.argv) > 1 else "01_authentic_gonorego_rate138_pbas-10.wav"
    normal = sys.argv[2] if len(sys.argv) > 2 else "hakka_normal.jpg"
    mouth_open = sys.argv[3] if len(sys.argv) > 3 else "hakka_sip.jpg"
    out = sys.argv[-1] if len(sys.argv) > 4 and sys.argv[-1].endswith(".mp4") else "preview_pure_mouse_gonorego.mp4"

    render_video(wav, normal, mouth_open, out)

import sys
import os
import wave
import random
import subprocess
import imageio_ffmpeg

def get_audio_duration(wav_path: str) -> float:
    try:
        with wave.open(wav_path, 'r') as w:
            return w.getnframes() / float(w.getframerate())
    except Exception as e:
        print(f"Error reading duration: {e}")
        return 60.0

def build_concat_file(normal_img: str, sip_img: str, total_duration: float, out_file: str):
    lines = []
    current_time = 0.0

    normal_img_abs = os.path.abspath(normal_img).replace("\\", "/")
    sip_img_abs = os.path.abspath(sip_img).replace("\\", "/") if os.path.exists(sip_img) else normal_img_abs

    rng = random.Random(42)

    while current_time < total_duration + 5.0:
        # Hakka talking / ranting (5.0 - 7.5s)
        talk_dur = rng.uniform(5.0, 7.5)
        lines.append(f"file '{normal_img_abs}'")
        lines.append(f"duration {talk_dur:.2f}")
        current_time += talk_dur

        # Hakka tilting glass / taking sip (1.4 - 1.8s)
        if os.path.exists(sip_img):
            sip_dur = rng.uniform(1.4, 1.8)
            lines.append(f"file '{sip_img_abs}'")
            lines.append(f"duration {sip_dur:.2f}")
            current_time += sip_dur

    lines.append(f"file '{normal_img_abs}'")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"=== Generated animation sequence -> {out_file} (Duration: {current_time:.1f}s) ===")

def render_video(wav_path: str, normal_img: str, sip_img: str, ass_path: str, out_mp4: str):
    duration = get_audio_duration(wav_path)
    concat_file = "frames.txt"
    build_concat_file(normal_img, sip_img, duration, concat_file)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using ffmpeg at: {ffmpeg_bin}")

    # Try with subtitles first
    if os.path.exists(ass_path):
        ass_abs = os.path.abspath(ass_path).replace("\\", "/").replace(":", "\\:")
        cmd = [
            ffmpeg_bin, "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-i", wav_path,
            "-vf", f"subtitles={ass_abs}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", out_mp4
        ]
        print("Executing ffmpeg with ASS subtitles:")
        print(" ".join(cmd))
        res = subprocess.run(cmd)
        if res.returncode == 0 and os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000:
            print("=== Successfully rendered video with Flash subtitles! ===")
            return

        print("Subtitles render returned non-zero code. Falling back to video without subtitles filter...")

    # Fallback without subtitles filter if libass is missing
    cmd_fallback = [
        ffmpeg_bin, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", wav_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", out_mp4
    ]
    print("Executing fallback ffmpeg without subtitles filter:")
    res = subprocess.run(cmd_fallback)
    if res.returncode != 0:
        raise RuntimeError("ffmpeg video rendering failed!")
    print("=== Successfully rendered video (fallback)! ===")

if __name__ == "__main__":
    wav = sys.argv[1] if len(sys.argv) > 1 else "output.wav"
    normal = sys.argv[2] if len(sys.argv) > 2 else "hakka_normal.jpg"
    sip = sys.argv[3] if len(sys.argv) > 3 else "hakka_sip.jpg"
    ass = sys.argv[4] if len(sys.argv) > 4 else "subtitles.ass"
    out = sys.argv[5] if len(sys.argv) > 5 else "output.mp4"

    render_video(wav, normal, sip, ass, out)

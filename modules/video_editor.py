import os
import subprocess

def get_audio_duration(audio_path):
    """Hàm phụ trợ: Dùng FFprobe để đo độ dài file mp3"""
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ Không thể đo độ dài audio, dùng mức mặc định 50s.")
        return 50.0

def render_final_video(video_paths: list, audio_path: str, srt_path: str, output_path: str, bgm_path: str = None):
    if not video_paths or not os.path.exists(audio_path) or not os.path.exists(srt_path):
        return None

    abs_srt = os.path.abspath(srt_path)
    safe_srt = abs_srt.replace('\\', '/').replace(':', r'\:')

    # ===== THUẬT TOÁN CHIA ĐỀU THỜI LƯỢNG =====
    audio_duration = get_audio_duration(audio_path)
    clip_duration = audio_duration / len(video_paths)
    print(f"   ⏱️ Giọng AI dài {audio_duration:.1f}s. Hệ thống sẽ cắt {len(video_paths)} cảnh, mỗi cảnh dài chính xác {clip_duration:.1f}s.")
    # ==========================================

    style_config = (
        "Fontname=Impact,Fontsize=14,PrimaryColour=&H0000FFFF&,"
        "OutlineColour=&H00000000&,BorderStyle=1,Outline=1.5,"
        "Alignment=2,MarginV=30"
    )

    inputs = []
    filter_complex = ""
    concat_labels = ""

    for i, vp in enumerate(video_paths):
        # MẸO PRO: Lệnh -stream_loop -1 và -t clip_duration
        # Nó bắt FFmpeg chạy video này, nếu video quá ngắn thì lặp lại, đúng tới mốc clip_duration thì cắt phăng!
        inputs.extend(["-stream_loop", "-1", "-t", str(clip_duration), "-i", os.path.abspath(vp)])
        
        filter_complex += f"[{i}:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=30[v{i}]; "
        concat_labels += f"[v{i}]"

    filter_complex += f"{concat_labels}concat=n={len(video_paths)}:v=1:a=0[concated]; "
    filter_complex += f"[concated]subtitles='{safe_srt}':force_style='{style_config}'[final_v]"

    audio_index = len(video_paths)
    inputs.extend(["-i", os.path.abspath(audio_path)])

    if bgm_path and os.path.exists(bgm_path):
        bgm_index = audio_index + 1
        inputs.extend(["-stream_loop", "-1", "-i", os.path.abspath(bgm_path)])
        filter_complex += f"; [{audio_index}:a]volume=2.0[tts]; [{bgm_index}:a]volume=0.1[bgm]; [tts][bgm]amix=inputs=2:duration=first[final_a]"
        audio_map = "[final_a]"
    else:
        audio_map = f"{audio_index}:a"

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[final_v]",
        "-map", audio_map,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        os.path.abspath(output_path)
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return output_path
        else:
            print(f"❌ FFmpeg error: {result.stderr[-500:]}")
            return None
    except Exception as e:
        print(f"❌ Hệ thống lỗi: {str(e)}")
        return None
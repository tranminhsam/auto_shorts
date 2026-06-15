import os
import subprocess

def render_final_video(video_paths: list, audio_path: str, srt_path: str, output_path: str, bgm_path: str = None):
    if not video_paths or not os.path.exists(audio_path) or not os.path.exists(srt_path):
        print("❌ Thừa hành thất bại: Thiếu file nguyên liệu.")
        return None

    abs_srt = os.path.abspath(srt_path)
    safe_srt = abs_srt.replace('\\', '/').replace(':', r'\:')

    # Vẫn giữ cấu hình phụ đề nhỏ, gọn, nằm dưới đáy video
    style_config = (
        "Fontname=Impact,"
        "Fontsize=14,"        
        "PrimaryColour=&H0000FFFF&,"
        "OutlineColour=&H00000000&,"
        "BorderStyle=1,"
        "Outline=1.5,"          
        "Alignment=2,"        
        "MarginV=30"         
    )

    # ===== THUẬT TOÁN HACK: NHÂN BẢN VIDEO ĐỂ LẶP LẠI =====
    # Nhân danh sách video lên 5 lần để đảm bảo hình ảnh luôn dài hơn âm thanh
    extended_video_paths = video_paths * 5 
    # =======================================================

    inputs = []
    filter_complex = ""
    concat_labels = ""

    # Nạp chuỗi video đã được nhân bản vào hệ thống
    for i, vp in enumerate(extended_video_paths):
        inputs.extend(["-i", os.path.abspath(vp)])
        # Ép tất cả khung hình về chuẩn 720x1280 để nối không bị lỗi
        filter_complex += f"[{i}:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,fps=30[v{i}]; "
        concat_labels += f"[v{i}]"

    # Nối tất cả các video lại
    filter_complex += f"{concat_labels}concat=n={len(extended_video_paths)}:v=1:a=0[concated]; "
    
    # Nướng phụ đề vào video
    filter_complex += f"[concated]subtitles='{safe_srt}':force_style='{style_config}'[final_v]"

    # Vị trí của file Audio sẽ nằm sau danh sách video
    audio_index = len(extended_video_paths)
    inputs.extend(["-i", os.path.abspath(audio_path)])

    # Xử lý trộn nhạc nền (BGM)
    if bgm_path and os.path.exists(bgm_path):
        bgm_index = audio_index + 1
        inputs.extend(["-stream_loop", "-1", "-i", os.path.abspath(bgm_path)])
        
        # duration=first đảm bảo nhạc nền bị ngắt đúng lúc giọng đọc kết thúc
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
        "-shortest", # Giờ đây lệnh shortest sẽ cắt chính xác vào giây cuối cùng của Audio
        os.path.abspath(output_path)
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"✅ RENDER VIDEO THÀNH CÔNG: {output_path}")
            return output_path
        else:
            print(f"❌ FFmpeg error: {result.stderr[-500:]}")
            return None
    except Exception as e:
        print(f"❌ Hệ thống lỗi: {str(e)}")
        return None
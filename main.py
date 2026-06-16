import os
import uuid
import shutil
from dotenv import load_dotenv

# Giữ nguyên toàn bộ cấu trúc import gốc của bạn
from modules.script_gen import generate_script
from modules.tts_engine import create_tts_and_subtitles
from modules.downloader import download_video_from_keyword
from modules.video_editor import render_final_video

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

def run_automated_shorts_pipeline(topic: str):
    working_dir = os.path.abspath(f"workspace/video_{os.urandom(4).hex()}")
    os.makedirs(working_dir, exist_ok=True)
    
    # [BƯỚC 1/4] KỊCH BẢN TỪNG CẢNH
    print(f"\n🧠 [Bước 1/4] Đang vắt óc suy nghĩ kịch bản và phân cảnh cho chủ đề: {topic}")
    script_data = generate_script(topic)
    
    if not script_data or "scenes" not in script_data:
        print("❌ Lỗi: Không thể khởi tạo kịch bản phân cảnh từ AI.")
        return None

    # Lắp ráp lại toàn bộ câu thoại để cho AI đọc một mạch
    full_text = " ".join([scene["narration"] for scene in script_data["scenes"]])
    
    # Rút trích danh sách từ khóa theo đúng thứ tự kịch bản từng cảnh
    scene_keywords = [scene["keyword"] for scene in script_data["scenes"]]
    
    script_path = os.path.join(working_dir, "script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print("✅ Đã chốt xong kịch bản và từ khóa bám sát từng câu thoại!")

   # [BƯỚC 2/4] TẠO GIỌNG ĐỌC VÀ PHỤ ĐỀ
    print("\n🎙️ [Bước 2/4] Đang thuê 'Diễn viên lồng tiếng AI' thu âm và tạo phụ đề...")
    
    # SỬA Ở ĐÂY: Chỉ định rõ tên file 'audio.mp3' thay vì chỉ đưa thư mục gốc
    audio_target = os.path.join(working_dir, "audio.mp3")
    
    # Truyền đường dẫn file cụ thể vào hàm gốc của bạn
    audio_path, srt_path = create_tts_and_subtitles(full_text, audio_target)
    
    if not audio_path or not srt_path:
        print("❌ Lỗi: Không thể khởi tạo giọng đọc hoặc phụ đề.")
        return None

    # [BƯỚC 3/4] TẢI VIDEO THEO TỪNG CÂU THOẠI
    print("\n📥 [Bước 3/4] Đang tải video minh họa siêu sát nghĩa cho từng cảnh...")
    downloaded_videos = []
    
    for idx, kw in enumerate(scene_keywords):
        print(f"   🔍 Cảnh {idx + 1}: Tìm video cho từ khóa '{kw}'")
        # Sử dụng đúng hàm download_video_from_keyword gốc từ modules.downloader
        vp = download_video_from_keyword(keyword=kw, output_dir=working_dir)
        
        # Nếu từ khóa này không tìm thấy video, dùng từ khóa dự phòng an toàn
        if not vp:
            print(f"   ⚠️ Không tìm thấy, dùng video dự phòng 'mystery'...")
            vp = download_video_from_keyword(keyword="mystery", output_dir=working_dir)
            
        if vp:
            downloaded_videos.append(vp)
            
    if not downloaded_videos:
        print("❌ Lỗi: Không tải được bất kỳ video nào.")
        return None

    # [BƯỚC 4/4] RENDER VIDEO
    print("\n🎬 [Bước 4/4] Đang khởi động FFmpeg để xử lý kỹ xảo và xuất bản video...")
    output_filename = f"{topic.replace(' ', '_')[:30]}_final.mp4"
    output_filepath = os.path.join("outputs", output_filename)
    os.makedirs("outputs", exist_ok=True)
    
    bgm_path = "bgm.mp3"
    if not os.path.exists(bgm_path):
        bgm_path = None
        
    # Sử dụng đúng hàm render_final_video gốc từ modules.video_editor
    final_video = render_final_video(downloaded_videos, audio_path, srt_path, output_filepath, bgm_path)
    
    if final_video:
        print(f"\n🎉 THÀNH CÔNG RỰC RỠ! Video đã ra lò tại: {final_video}")
        return final_video
    else:
        print("\n❌ Thất bại ở khâu Render cuối cùng.")
        return None


import os
import uuid
import shutil
from dotenv import load_dotenv

from modules.script_gen import generate_script
from modules.tts_engine import create_tts_and_subtitles
from modules.downloader import download_video_from_keyword
from modules.video_editor import render_final_video

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()

def run_automated_shorts_pipeline(topic: str):
    video_id = str(uuid.uuid4())[:8]
    working_dir = os.path.join("workspace", f"video_{video_id}")
    os.makedirs(working_dir, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    audio_path = os.path.join(working_dir, "audio.mp3")
    srt_path = os.path.join(working_dir, "subtitles.srt")
    final_video_path = os.path.join("outputs", f"final_shorts_{video_id}.mp4")

    print("="*50)
    print(f"🚀 KHỞI CHẠY PIPELINE TỰ ĐỘNG HÓA CHỦ ĐỀ: '{topic}'")
    print("="*50)

    try:
        print("\n🧠 [Bước 1/4] Đang gửi yêu cầu cho Gemini sáng tạo nội dung...")
        script_data = generate_script(topic)
        if not script_data:
            print("❌ Lỗi: Không thể khởi tạo kịch bản từ AI.")
            return
            
        script_text = script_data.get("full_text")
        keywords = script_data.get("visual_keywords", [])
        print(f"📝 Kịch bản đã viết xong (Độ dài: {len(script_text)} ký tự).")

        print("\n🎙️ [Bước 2/4] Đang chuyển đổi văn bản sang giọng nói và trích xuất phụ đề...")
        audio_result, srt_result = create_tts_and_subtitles(text=script_text, audio_output=audio_path, sub_output=srt_path)
        
        if not audio_result or not srt_result:
            print("❌ DÂY CHUYỀN DỪNG LẠI: Module giọng đọc và phụ đề gặp sự cố!")
            return
            
        print("🎵 Đã tạo xong file audio.mp3 và file subtitles.srt.")

        print("\n📥 [Bước 3/4] Đang kích hoạt Bot lên Pexels săn tìm chuỗi video B-roll chuyển cảnh...")
        downloaded_videos = []
        for kw in keywords[:6]:
            print(f"   🔍 Tìm video cho cảnh: '{kw}'")
            vp = download_video_from_keyword(keyword=kw, output_dir=working_dir)
            if vp and vp not in downloaded_videos:
                downloaded_videos.append(vp)
                
        if not downloaded_videos:
            print("⚠️ Không tìm thấy video đúng từ khóa, đang tải video vũ trụ/thiên nhiên dự phòng...")
            downloaded_videos.append(download_video_from_keyword(keyword="universe", output_dir=working_dir))

        print(f"📥 Đã tải thành công {len(downloaded_videos)} video B-roll.")

        print("\n🎬 [Bước 4/4] Đang khởi động FFmpeg để xử lý kỹ xảo và xuất bản video...")
        
        # KIỂM TRA FILE NHẠC NỀN
        bgm_file = "bgm.mp3"
        bgm_path = bgm_file if os.path.exists(bgm_file) else None
        
        if bgm_path:
            print("   🎧 Đã phát hiện nhạc nền, đang tiến hành trộn âm thanh (Audio Mixing)...")
        else:
            print("   ⚠️ Không tìm thấy file 'bgm.mp3' trong thư mục gốc, sẽ chỉ dùng giọng đọc AI.")

        result_path = render_final_video(
            video_paths=downloaded_videos, 
            audio_path=audio_path,
            srt_path=srt_path,
            output_path=final_video_path,
            bgm_path=bgm_path # Bơm đường dẫn nhạc nền vào hệ thống
        )
        
        if result_path:
            print("\n" + "="*50)
            print(f"🎉 XUẤT BẢN THÀNH CÔNG! Video Shorts của bạn đã sẵn sàng tại:")
            print(f"📁 {result_path}")
            print("="*50)
# DÒNG THÊM MỚI QUAN TRỌNG: Trả đường dẫn video về cho hệ thống Web
            return result_path
    except Exception as e:
        print(f"\n❌ Hệ thống gặp sự cố nghiêm trọng tại dây chuyền: {str(e)}")
    finally:
        if os.path.exists(working_dir):
            print("\n🧹 Đang dọn dẹp các file rác trong workspace...")
            shutil.rmtree(working_dir)

if __name__ == "__main__":
    user_topic = input("Nhập chủ đề video bạn muốn làm bằng tiếng Anh: ")
    if user_topic.strip():
        run_automated_shorts_pipeline(user_topic)
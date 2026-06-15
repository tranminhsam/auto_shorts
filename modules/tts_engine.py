import asyncio
import edge_tts
import os
import re

async def generate_audio_and_subs(text: str, audio_path: str, srt_path: str, is_retry=False):
    # GIỌNG STEFFAN: Trầm ấm, kể chuyện lôi cuốn, điện ảnh
    voice = "en-US-SteffanNeural" 
    
    # MẸO 1: "Tắm rửa" kịch bản, xóa sạch khoảng trắng thừa và ký tự gây nghẽn máy chủ
    clean_text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    communicate = edge_tts.Communicate(clean_text, voice)
    words_list = []
    
    # Cố gắng lấy mốc thời gian từng từ (Karaoke)
    with open(audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_ticks = chunk["offset"]
                duration_ticks = chunk["duration"]
                word = chunk["text"]
                
                time_start = edge_tts.formatter(start_ticks)
                time_end = edge_tts.formatter(start_ticks + duration_ticks)
                words_list.append((time_start, time_end, word))
                
    # NẾU THÀNH CÔNG: Ghi ra file SRT dạng nhảy chữ
    if words_list:
        with open(srt_path, "w", encoding="utf-8") as srt_file:
            for i, (start, end, word) in enumerate(words_list):
                srt_start = start.replace(".", ",")
                srt_end = end.replace(".", ",")
                
                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{srt_start} --> {srt_end}\n")
                clean_word = word.strip(".,!?\"'()").upper()
                srt_file.write(f"{clean_word}\n\n")
        return True
        
    # MẸO 2: CƠ CHẾ ĐÁNH LỪA MÁY CHỦ BẰNG CÁCH NGỦ ĐÔNG
    if not is_retry:
        print("   ⏳ Máy chủ Edge nghi ngờ bot. Đang ngắt kết nối và giả vờ ngủ 3 giây...")
        await asyncio.sleep(3) # Nghỉ 3 giây để làm mới tín hiệu
        print("   🔄 Đang kết nối lại luồng Karaoke...")
        # Đệ quy gọi lại chính hàm này một lần nữa
        return await generate_audio_and_subs(text, audio_path, srt_path, is_retry=True)
        
    # NẾU THỬ LẠI VẪN THẤT BẠI -> FALLBACK PHỤ ĐỀ CÂU
    print("   ⚠️ Máy chủ vẫn đóng băng WordBoundary. Tự động chuyển sang phụ đề câu...")
    submaker = edge_tts.SubMaker()
    with open(audio_path, "wb") as audio_file:
        async for chunk in edge_tts.Communicate(clean_text, voice).stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            else:
                submaker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.write(submaker.get_srt())
    return True

def create_tts_and_subtitles(text: str, audio_output="audio.mp3", sub_output="subtitles.srt"):
    try:
        success = asyncio.run(generate_audio_and_subs(text, audio_output, sub_output))
        if success:
            return audio_output, sub_output
        return None, None
    except Exception as e:
        print(f"❌ Lỗi tạo audio/sub: {str(e)}")
        return None, None
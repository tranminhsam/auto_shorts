import os
import requests
from dotenv import load_dotenv

# Tải cấu hình API Key từ file .env
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def download_video_from_keyword(keyword: str, output_dir: str = "test_assets"):
    """
    Tự động kết nối API Pexels, tìm kiếm 1 video dọc (9:16) 
    phù hợp với từ khóa và tải file .mp4 về máy.
    """
    if not PEXELS_API_KEY:
        print("❌ Lỗi: Chưa cấu hình PEXELS_API_KEY trong file .env")
        return None

    # Tự động tạo thư mục chứa video tải về nếu chưa có
    os.makedirs(output_dir, exist_ok=True)
    
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "per_page": 1,            # Chỉ lấy 1 video tốt nhất để tiết kiệm băng thông
        "orientation": "portrait"  # LƯU Ý: Ép Pexels chỉ trả về video khung hình dọc 9:16 cho Shorts
    }

    try:
        # Gọi API tìm kiếm video
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Lỗi kết nối Pexels (Mã lỗi {response.status_code})")
            return None

        data = response.json()
        videos = data.get("videos", [])
        if not videos:
            print(f"⚠️ Không tìm thấy video dọc nào khớp với từ khóa: '{keyword}'")
            return None

        # Trích xuất thông tin video đầu tiên tìm được
        first_video = videos[0]
        video_files = first_video.get("video_files", [])

        # Chọn link video chất lượng HD (tránh bản 4K quá nặng, hoặc bản SD quá mờ)
        video_url = None
        for file_info in video_files:
            if file_info.get("quality") == "hd":
                video_url = file_info.get("link")
                break
        
        # Nếu không có tag 'hd', lấy đại link đầu tiên hệ thống cung cấp
        if not video_url and video_files:
            video_url = video_files[0].get("link")

        if video_url:
            # Chuẩn hóa tên file bằng cách thay khoảng trắng bằng dấu gạch dưới
            safe_file_name = f"{keyword.replace(' ', '_')}.mp4"
            final_file_path = os.path.join(output_dir, safe_file_name)
            
            print(f"📥 Đang tải video B-roll cho từ khóa '{keyword}'...")
            
            # Tiến hành tải luồng file (stream) về ổ cứng
            video_response = requests.get(video_url, stream=True)
            with open(final_file_path, "wb") as video_file:
                for chunk in video_response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        video_file.write(chunk)
                        
            print(f"✅ TẢI THÀNH CÔNG: {final_file_path}")
            return final_file_path

    except Exception as e:
        print(f"❌ Lỗi trong quá trình tải tài nguyên: {str(e)}")
        return None

# ---- ĐOẠN CODE DÙNG ĐỂ CHẠY THỬ NGHIỆM ĐỘC LẬP MODULE 3 ----
if __name__ == "__main__":
    print("--- Thử nghiệm chạy độc lập Module 3 ---")
    
    # Từ khóa thử nghiệm bối cảnh không gian điện ảnh
    test_keyword = "nebula galaxy" 
    
    # Chạy hàm tải video
    download_video_from_keyword(test_keyword)
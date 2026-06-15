import streamlit as st
import os
import time

# Import lõi hệ thống
from main import run_automated_shorts_pipeline

st.set_page_config(page_title="Bulk AI Shorts Generator", page_icon="🎬", layout="centered")

st.title("🎬 Hệ Thống Tạo Video Shorts Hàng Loạt")
st.markdown("Nhập nhiều chủ đề cùng lúc (mỗi dòng một chủ đề). Hệ thống sẽ tự động xử lý cuốn chiếu từng video một.")

# Thay thế st.text_input bằng st.text_area để nhập nhiều dòng
bulk_topics_raw = st.text_area(
    "💡 Nhập danh sách chủ đề của bạn (Mỗi dòng là 1 video độc lập):",
    height=200,
    placeholder="3 terrifying facts about deep ocean\n5 common mistakes in English\nHow to speak English fluently"
)

if st.button("🚀 Kích Hoạt Chạy Hàng Loạt (Bulk Generate)", type="primary"):
    # Xử lý tách chuỗi văn bản thành danh sách các chủ đề, loại bỏ dòng trống
    topics = [t.strip() for t in bulk_topics_raw.split("\n") if t.strip()]
    
    if not topics:
        st.warning("⚠️ Vui lòng nhập ít nhất một chủ đề!")
    else:
        total_videos = len(topics)
        st.info(True and f"📋 Đã ghi nhận {total_videos} chủ đề. Bắt đầu tiến trình sản xuất tự động...")
        
        # Tạo thanh tiến trình tổng quan
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        
        # Vòng lặp quét qua từng chủ đề một (Cuốn chiếu)
        for index, topic in enumerate(topics):
            current_num = index + 1
            status_text.markdown(f"### ⏳ [Video {current_num}/{total_videos}] Đang xử lý: *{topic}*")
            
            # Sử dụng st.status để gom nhóm các log chạy của main.py cho gọn giao diện
            with st.status(f"Chi tiết tiến trình Video {current_num}...", expanded=True) as status:
                try:
                    start_time = time.time()
                    # Gọi lõi xử lý hệ thống cho chủ đề hiện tại
                    video_output_path = run_automated_shorts_pipeline(topic)
                    end_time = time.time()
                    
                    if video_output_path and os.path.exists(video_output_path):
                        success_count += 1
                        status.write(f"✅ Hoàn thành trong {round(end_time - start_time, 1)}s")
                        status.write(f"📁 Lưu tại: `{video_output_path}`")
                        status.update(label=f"🟢 Video {current_num}: Thành công!", state="complete")
                        
                        # Hiển thị video thành phẩm ngay trên Web để xem trước
                        st.video(video_output_path)
                    else:
                        status.update(label=f"🔴 Video {current_num}: Thất bại ở bước xử lý.", state="error")
                except Exception as e:
                    status.write(f"❌ Lỗi hệ thống: {str(e)}")
                    status.update(label=f"🔴 Video {current_num}: Gặp sự cố nghiêm trọng.", state="error")
            
            # Cập nhật thanh tiến trình tổng thể sau khi xong 1 video
            overall_progress.progress(current_num / total_videos)
            
        st.success(f"🎉 Hoàn thành chiến dịch! Đã sản xuất thành công {success_count}/{total_videos} video Shorts.")
import streamlit as st
import os
from main import run_automated_shorts_pipeline

# Cấu hình giao diện trang web
st.set_page_config(page_title="Auto Shorts AI", page_icon="🎬", layout="centered")

st.title("🎬 Hệ Thống Tạo Video Shorts Tự Động")
st.markdown("Nhập chủ đề bạn muốn, AI sẽ tự động viết kịch bản, đọc giọng, tìm video B-roll và dựng thành phẩm chỉ với 1 click.")

# Ô nhập liệu
topic = st.text_input("💡 Nhập chủ đề video:", placeholder="Ví dụ: The terrifying scale of the blue whale")

# Nút bấm 1-click
if st.button("🚀 Tạo Video Ngay", use_container_width=True):
    if not topic.strip():
        st.warning("⚠️ Vui lòng nhập chủ đề trước khi bấm tạo!")
    else:
        # Bật hiệu ứng loading chờ đợi
        with st.spinner("Đang sản xuất video... Quá trình này có thể mất 1-3 phút. (Bạn có thể xem tiến trình chi tiết trên Terminal)"):
            try:
                # Gọi hàm lõi từ file main.py
                final_video_path = run_automated_shorts_pipeline(topic)
                
                if final_video_path and os.path.exists(final_video_path):
                    st.success(f"🎉 Thành công! Video đã được lưu tại: `{final_video_path}`")
                    
                    # Hiển thị video để xem trước ngay trên trình duyệt
                    st.video(final_video_path)
                    
                    # Thêm nút tải xuống tiện lợi
                    with open(final_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ Tải Video Về Máy",
                            data=file,
                            file_name=os.path.basename(final_video_path),
                            mime="video/mp4",
                            use_container_width=True
                        )
                else:
                    st.error("❌ Có lỗi xảy ra ở khâu render. Vui lòng kiểm tra Terminal để xem chi tiết.")
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {str(e)}")
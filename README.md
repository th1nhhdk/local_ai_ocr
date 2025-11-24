<img src='src/icon.png' width='128' height='128'>

# Local AI OCR (v1.5)

Một phần mềm OCR offline (sau khi thiết lập lần đầu), portable, có thể xử lý ảnh và file PDF nhờ việc sử dụng AI nội bộ **DeepSeek-OCR**.

## Tính năng

- **Chạy offline (nội bộ):** Không cần kết nối mạng, đảm bảo bảo mật dữ liệu.
- **Tự quyết định Ngôn ngữ phần mềm:** dựa vào việc máy có `Cốc Cốc` hoặc `Zalỏ` hay không.
- **Hỗ trợ GPU (hoặc CPU):** Tự động phát hiện và sử dụng GPU để tăng tốc, tự động chuyển sang CPU nếu không thể sử dụng GPU (CPU sẽ chậm hơn nhiều).
- **Hỗ trợ nhiều định dạng file:** Ảnh `.png`, `.jpg`, `.webp` và Tài liệu `.pdf`.
- **Xử lý PDF thông minh:** Cho phép chọn phạm vi trang để xử lý (với các tệp PDF >=2 trang).
- **Có 3 chế độ xử lý:**
  - **OCR Tiêu chuẩn:** Trích xuất văn bản, cố giữ bố cục gốc.
  - **OCR không bố cục (Free OCR):** Trích xuất văn bản, không giữ bố cục (bố cục tự do).
  - **Tài liệu Markdown (HTML nặng):** Trích xuất văn bản ra định dạng Markdown
    - **Cảnh báo:** Chế độ này có thể tạo ra rất nhiều tag HTML tùy vào tài liệu được cho
    - *Mẹo:* Hãy sử dụng AI khác để dọn dẹp kết quả.
- **Hệ thống Hàng chờ:** Cho phép xử lý lần lượt nhiều file (không nên dùng quá 15 file cùng lúc vì có thể sẽ bị kẹt trong vòng lập vô tận)
- **Tự động xả Model AI để giải phóng bộ nhớ:** Sau khi `Bắt đầu xử lý` lần đầu thì Model AI sẽ được nạp vào bộ nhớ, đợi 5 phút sau khi hoàn thành thì bộ nhớ sẽ tự được giải phóng.

## Yêu cầu hệ thống

- **OS:** Windows 10 trở lên
- **CPU:** Tối thiểu 4 lõi/8 luồng
- **RAM:** Tối thiểu 16GB
- **Dung lượng trống:** Khoảng 12GB
- **GPU:** Có GPU (nên dùng Nvidia), với tối thiểu 8GB VRAM
  - **Lưu ý:** Nếu không có GPU đạt yêu cầu thì phần mềm sẽ sử dụng CPU (chậm hơn nhiều)

## Tải về và thiết lập

0. Tải file `.zip` trong mục Releases (bên phải, dưới About), giải nén nó ra
1. Chạy `env_setup.bat`
   - **Lưu ý:** Script này sẽ tải về file (weights) AI nặng 6.67 GB

- Bạn đã hoàn thành việc thiết lập phần mềm, phần mềm sẽ không cần kết nối mạng nữa.

## Lưu ý trước khi sử dụng

- Vì giới hạn kỹ thuật, AI OCR **có thể bị kẹt** trong vòng lặp vô hạn. Nếu chuyện đó xảy ra, hãy nhấn **DỪNG LẠI**.
- Mặc dù `DeepSeek-OCR` có độ chính xác cực cao, bạn **vẫn nên kiểm tra lại kết quả**, đặc biệt với tài liệu quan trọng.
- Lần chạy đầu tiên luôn tốn một chút thời gian để load AI Model vào bộ nhớ.

## Hướng dẫn sử dụng

1. **Khởi động phần mềm:**
   - Chạy file `run.bat` để khởi động ứng dụng (sử dụng GPU nếu có thể).
   - Nếu bạn muốn ép phần mềm chạy bằng CPU, hãy dùng `run_cpu-only.bat`.

2. **Sử dụng phần mềm:**
   - **2a. Quản lý tệp tin:**
      + Thêm ảnh/Thêm PDF: Chọn tài liệu cần xử lý để thêm vào Hàng chờ xử lý.
      + Xóa sạch Hàng chờ: Xóa sạch danh sách Hàng chờ xử lý.
   - **2b. Cài đặt (nên giữ mặc định):** Chọn giữa 3 chế độ OCR, mặc định (OCR Tiêu chuẩn) là tốt nhất.
   - **2c. Bắt đầu OCR:** Nhấn nút "Bắt đầu xử lý" để AI bắt đầu OCR.
   - **2d. Kết quả:** Văn bản sau khi được xử lý sẽ hiển thị nội dung ở khung bên phải.
   - **2e. Sao chép kết quả:** Nhấn nút này để sao chép nội dung trong ô Kết quả, bạn có thể dán vào Word hoặc phần mềm khác.

- *Mẹo*: Nút "`Unload Model AI`" giúp giải phóng RAM/VRAM khi bạn không sử dụng OCR nữa mà chưa muốn tắt ứng dụng.

## Xử lý vấn đề

- Nếu bạn gặp lỗi liên quan đến GPU, hãy dùng `run_cpu-only.bat` thay vì `run.bat` để phần mềm không sử dụng GPU.
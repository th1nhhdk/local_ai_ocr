![Local AI OCR icon](src/icon.png)

# Local AI OCR

Một công cụ OCR offline, có thể xử lý file ảnh và pdf, sử dụng sức mạnh của AI nội bộ (DeepSeek-OCR).

## Tính năng

- **Chạy offline trực tiếp trên máy**: Không cần kết nối mạng, ảnh/tài liệu của bạn luôn ở trên máy.
- **Hỗ trợ nhiều định dạng**: `.png`, `.jpg`, `.webp` và `.pdf`.
- Quyết định Ngôn ngữ mặc định dựa vào việc máy có `Cốc Cốc` / `Zalỏ` hay không.
- **Có 3 chế độ xử lý**:
  - **OCR Tiêu chuẩn**: Trích xuất văn bản.
  - **Tài liệu Markdown (HTML nặng)**: OCR ra định dạng Markdown (**Cảnh báo:** Chế độ này có thể tạo ra rất nhiều tag HTML tùy vào tài liệu (Mẹo: Hãy sử dụng AI khác để dọn dẹp kết quả).
  - **OCR không bố cục (Free OCR)**: OCR tự do, không giữ bố cục.
- **Có thể xử lý hàng loạt**: Thêm nhiều file vào hàng chờ và phần mềm sẽ tự động xử lý hết (**Không nên** dùng quá 10 file cùng lúc).

## Yêu cầu hệ thống

Nếu có GPU rời: **Phải là GPU Nvidia**, không hỗ trợ AMD

### Có GPU rời với VRAM >= 4GB
- Dung lượng trống: khoảng 5.5GB
- GPU sẽ gánh hết việc chạy AI OCR

### Không có GPU rời / GPU rời rất yếu (< 4GB VRAM)
- Dung lượng trống: khoảng 5.5GB
- RAM: ít nhất 8GB
- CPU: tối thiểu 4 lõi/8 luồng
- CPU sẽ gánh hết việc chạy AI OCR

## Sử dụng

0. Tải file `.zip` trong Releases (bên Phải), giải nén nó ra
1. Chạy file `run.ps1` (Nhấn chuột phải -> **Run with PowerShell**).
2. Chọn ngôn ngữ ở bên trên phải (nếu cần).
3. Nhấn **Thêm Ảnh** hoặc **Thêm PDF** để chọn tài liệu cần xử lý.
4. Chế độ xử lý mặc định là `OCR Tiêu chuẩn`, thay đổi nếu cần.
5. Nhấn **Bắt đầu xử lý**.
6. Kết quả sẽ hiển thị ở khung bên phải, nhấn **Sao chép kết quả** để lưu vào Clipboard.
** LƯU Ý: VUI LÒNG KIỂM TRA LẠI KẾT QUẢ, ĐẶC BIỆT KHI CÓ THÔNG TIN QUAN TRỌNG.**

## Sử dụng phần mềm với Model Chậm (Độ chính xác cao) **(Dành cho máy khỏe)**

Model Chậm mang lại độ chính xác cao hơn rất nhiều so với Model Nhanh (kèm theo phần mềm), nhưng nó sẽ chạy chậm hơn và tốn nhiều bộ nhớ máy hơn.
Nên sử dụng với máy có GPU rời và VRAM >= 8GB.

0. Tải file `.zip` trong Releases (bên Phải), giải nén nó ra
1. Chạy file `get_fp16_model.ps1` (Nhấn chuột phải -> **Run with PowerShell**), nó sẽ tải Model Chậm, chiếm 6.7GB dung lượng.
2. Chạy file `run.ps1` (Nhấn chuột phải -> **Run with PowerShell**).
3. Chọn ngôn ngữ ở bên trên phải (nếu cần).
4. Chọn `Model` (ở bên trên trái) là `deepseek-ocr:3b`.
5. Nhấn **Thêm Ảnh** hoặc **Thêm PDF** để chọn tài liệu cần xử lý.
6. Chế độ xử lý mặc định là `OCR Tiêu chuẩn`, thay đổi nếu cần.
7. Nhấn **Bắt đầu xử lý**.
8. Kết quả sẽ hiển thị ở khung bên phải, nhấn **Sao chép kết quả** để lưu vào Clipboard.

Nếu bạn đổi ý và muốn xóa AI Độ chính xác cao, hãy chạy file `remove_fp16_model.ps1` (Nhấn chuột phải -> **Run with PowerShell**).

## Xử lý vấn đề

Nếu bạn gặp vấn đề sau khi nhấn **Bắt đầu xử lý** và bạn có GPU rời nhưng nó rất cũ, hãy thử chạy `run_cpu-only.ps1` thay vì `run.ps1`. (Nhấn chuột phải -> **Run with PowerShell**)
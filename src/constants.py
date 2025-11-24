# src/constants.py
OLLAMA_HOST_DEFAULT = "http://127.0.0.1:11435"
DEFAULT_MODEL = "deepseek-ocr:3b"

# Used by stream_ocr_response()
PROMPTS = {
    "p_ocr":      "OCR this image.",
    "p_free":     "Free OCR.",
    "p_markdown": "<|grounding|>Convert the document to markdown.",
}

# Used by show_about() in gui.py
APP_VERSION = "v1.5"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local_ai_ocr" 

TRANSLATIONS = {
    "English": {
        "btn_add_img": "Add Images",
        "btn_add_pdf": "Add PDF",
        "btn_clear": "Clear Queue",
        "btn_stop": "STOP",
        "lbl_queue": "Processing Queue:",
        "group_settings": "Settings",
        "lbl_prompt": "Select Mode:",
        "btn_run": "Start Processing",
        "btn_copy": "Copy Output",
        "lbl_output": "Output:",
        "msg_done": "Processing complete.",
        "msg_error": "Error",
        "status_ready": "Start Processing ({})",
        "status_stopped": "Stopped by user.",

        "msg_elapsed": "Done in: {:.2f}s",
        "msg_total":   "Total Time: {:.2f}s",
        "msg_markdown_warn": (
            "<b>Warning:</b> This mode many generate a lot of HTML tags depending on the document.<br>"
            "(Tip: Use other AI to clean the output)."
        ),
        "msg_loop_disclaimer": (
            "<b>Disclaimer:</b> Due to technical limitations, the OCR AI <b>might get stuck</b> in an infinite loop.<br>"
            "If that happens please press <b>STOP</b>."
        ),

        "dlg_page_range_title": "Select Page Range",
        "dlg_page_range_msg": (
            "File: {}<br>"
            "Total Pages: {}<br><br>"
            "Select pages to import:"
        ),
        "dlg_page_range_start": "Start Page:",
        "dlg_page_range_end": "End Page:",
        "dlg_page_range_error": "<b>Error:</b> Start page cannot be greater than End page.",

        "btn_about": "About",
        "about_title": "About",
        "about_text": (
            "<center>"
            "<img src='{}' width='64' height='64'><br>"
            "<b>Local AI OCR</b>"
            "</center>"
            "<b>Version:</b> {}<br>"
            "<b>Author:</b> {}"
        ),
        "btn_about_github": "GitHub",

        "prompt_labels": {
            "p_ocr":      "Standard OCR",
            "p_free":     "OCR with No Layout (Free OCR)",
            "p_markdown": "Markdown Document (with heavy HTML)",
        },
        "lbl_proofread": "Please proofread the output, especially when there are important information.",

        "btn_unload": "Unload AI Model",
        "msg_model_unloaded": "AI Model unloaded from memory.",
        "msg_model_not_loaded": "AI Model is not currently loaded.",
    },
    "Tiếng Việt": {
        "btn_add_img": "Thêm ảnh",
        "btn_add_pdf": "Thêm PDF",
        "btn_clear": "Xóa sạch Hàng chờ",
        "btn_stop":  "DỪNG LẠI",
        "lbl_queue": "Hàng chờ xử lý:",
        "group_settings": "Cài đặt",
        "lbl_prompt": "Chọn chế độ:",
        "btn_run": "Bắt đầu xử lý",
        "btn_copy": "Sao chép kết quả",
        "lbl_output": "Kết quả:",
        "msg_done": "Hoàn tất xử lý.",
        "msg_error": "Lỗi",
        "status_ready": "Bắt đầu xử lý ({})",
        "status_stopped": "Đã được dừng lại bởi người dùng.",
        
        "msg_elapsed": "Hoàn thành trong: {:.2f}s",
        "msg_total":   "Tổng thời gian: {:.2f}s",
        "msg_markdown_warn": (
            "<b>Cảnh báo:</b> Chế độ này có thể tạo ra rất nhiều tag HTML tùy vào tài liệu.<br>"
            "(Mẹo: Hãy sử dụng AI khác để dọn dẹp kết quả)."
        ),
        "msg_loop_disclaimer": (
            "<b>Lưu ý:</b> Vì giới hạn kỹ thuật, AI OCR <b>có thể bị kẹt</b> trong vòng lặp vô hạn.<br>"
            "Nếu chuyện đó xảy ra, hãy nhấn <b>DỪNG LẠI</b>."
        ),

        "dlg_page_range_title": "Chọn Phạm vi Trang",
        "dlg_page_range_msg": (
            "Tập tin: {}<br>"
            "Tổng số trang: {}<br><br>"
            "Chọn trang cần nhập:"
        ),
        "dlg_page_range_start": "Từ trang:",
        "dlg_page_range_end": "Đến trang:",
        "dlg_page_range_error": "<b>Lỗi:</b> Trang bắt đầu không thể lớn hơn trang kết thúc.",

        "btn_about": "Giới thiệu",
        "about_title": "Giới thiệu",
        "about_text": (
            "<center>"
            "<img src='{}' width='64' height='64'><br>"
            "<b>Local AI OCR</b>"
            "</center>"
            "<b>Phiên bản:</b> {}<br>"
            "<b>Tác giả:</b> {}"
        ),
        "btn_about_github": "GitHub",

        "prompt_labels": {
            "p_ocr":      "OCR Tiêu chuẩn",
            "p_free":     "OCR không bố cục (Free OCR)",
            "p_markdown": "Tài liệu Markdown (HTML nặng)",
        },
        "lbl_proofread": "Vui lòng kiểm tra lại kết quả, đặc biệt khi có thông tin quan trọng.",

        "btn_unload": "Xả Model AI",
        "msg_model_unloaded": "Đã giải phóng Model AI khỏi bộ nhớ.",
        "msg_model_not_loaded": "Model AI hiện không có trong bộ nhớ.",
    }
}
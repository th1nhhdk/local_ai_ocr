# src/constants.py
OLLAMA_HOST_DEFAULT = "http://127.0.0.1:11435"

# Used by stream_ocr_response()
PROMPTS = {
    "p_ocr":      "OCR this image.",
    "p_markdown": "<|grounding|>Convert the document to markdown.",
    "p_free":     "Free OCR.",
}

# Used by show_about() in gui.py
APP_VERSION = "v1.0.0"
APP_AUTHOR = "Nguyễn Phước Thịnh"
PROJECT_URL = "https://github.com/th1nhhdk/local-ai-ocr" 

TRANSLATIONS = {
    "English": {
        "btn_add_img": "Add Images",
        "btn_add_pdf": "Add PDF",
        "btn_clear": "Clear Queue",
        "btn_stop":  "STOP",
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
        "msg_markdown_warn": "<b>Warning:</b> This mode many generate a lot of HTML tags depending on the document (Tip: Use other AI to clean the output).",
        "msg_loop_disclaimer": "<b>Disclaimer:</b> Due to technical limitations, the OCR AI <b>might get stuck</b> in an infinite loop. If that happens please press <b>STOP</b>.",

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
        "btn_github": "GitHub",

        "prompt_labels": {
            "p_ocr":      "Standard OCR",
            "p_markdown": "Markdown Document (with heavy HTML)",
            "p_free":     "OCR with No Layout (Free OCR)",
        },
        "lbl_proofread": "Please proofread the output, especially when there are important information.",

        "btn_model_fast": "Fast but more inaccurate",
        "btn_model_slow": "Slow but more accurate",
        "msg_model_fast_info": (
            "<b>Disclaimer:</b> This Model (q4_K_M) is faster but less accurate.<br>"
            "This Model <b>tends to get stuck</b> in a infinite loop. Please use the <b>Slow Model</b> if possible."
        ),
        "msg_model_slow_info": (
            "<b>Info:</b> This Model is slower but offers higher accuracy.<br>"
            "However, this Model <b>might get stuck</b> in a infinite loop because of technical limitations."
        ),
    },
    "Tiếng Việt": {
        "btn_add_img": "Thêm Ảnh",
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
        "msg_markdown_warn": "<b>Cảnh báo:</b> Chế độ này có thể tạo ra rất nhiều tag HTML tùy vào tài liệu (Mẹo: Hãy sử dụng AI khác để dọn dẹp kết quả).",
        "msg_loop_disclaimer": "<b>Lưu ý:</b> Vì giới hạn kỹ thuật, AI OCR <b>có thể bị kẹt</b> trong vòng lặp vô hạn. Nếu chuyện đó xảy ra, hãy nhấn <b>DỪNG LẠI</b>.",

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
        "btn_github": "GitHub",

        "prompt_labels": {
            "p_ocr":      "OCR Tiêu chuẩn",
            "p_markdown": "Tài liệu Markdown (HTML nặng)",
            "p_free":     "OCR không bố cục (Free OCR)",
        },
        "lbl_proofread": "Vui lòng kiểm tra lại kết quả, đặc biệt khi có thông tin quan trọng.",

        "btn_model_fast": "Nhanh nhưng kém chính xác",
        "btn_model_slow": "Chậm mà chính xác hơn",
        "msg_model_fast_info": (
            "<b>Lưu ý:</b> Model này (q4_K_M) nhanh hơn độ chính xác thấp hơn.<br>"
            "Model này <b>dễ bị kẹt</b> trong vòng lặp vô hạn. Hãy dùng <b>Model Chậm</b> nếu có thể."
        ),
        "msg_model_slow_info": (
            "<b>Thông tin:</b> Model này chậm nhưng cung cấp độ chính xác cao hơn.<br>"
            "Dù thế, Model này vẫn <b>có thể bị kẹt</b> trong vòng lặp vô hạn do giới hạn kỹ thuật."
        ),
    }
}
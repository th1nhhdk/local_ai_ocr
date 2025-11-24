# src/lang_handler.py
import os

# Guess the default language based on installed applications
def get_default_language():
    coccoc_path = r"C:\Program Files\CocCoc\Browser\Application\browser.exe"

    # Zalỏ is installed in the current user's AppData directory, not Program Files
    zalo_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Zalo", "Zalo.exe")

    if os.path.exists(coccoc_path) or os.path.exists(zalo_path):
        return "Tiếng Việt"

    return "English"
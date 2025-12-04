# src/lang_handler.py

import os
import json

# Map display names to filenames
LANGUAGES = {
    "English": "en",
    "Tiếng Việt": "vi"
}

def get_default_language():
    # Guesses the default language code nased on installed apps.
    coccoc_path = r"C:\Program Files\CocCoc\Browser\Application\browser.exe"

    # Zalỏ is installed in the current user's AppData directory, not Program Files
    zalo_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Programs", "Zalo", "Zalo.exe")

    if os.path.exists(coccoc_path) or os.path.exists(zalo_path):
        return "vi"

    return "en"

def get_available_languages():
    return LANGUAGES

def load_language(lang_code):
    # Resolve path relative to this file
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, "i18n", f"{lang_code}.json")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

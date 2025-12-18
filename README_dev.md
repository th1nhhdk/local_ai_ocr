<img src='src/res/icon.png' width='128' height='128'>

# Local AI OCR (v2.1.1)

## Tech Stack
- **wget2:** `2.2.0`
- **Python:** Embeddable Python `3.13.11`
- **Ollama:** `0.13.4`
- **deepseek-ocr:3b:** `0e7b018b8a22`
- **Frontend:** PySide6 `6.10.1`
- **src/res/node/mathjax:** `4.0.0`
- **src/res/node/@mathjax/mathjax-newcm-font:** `4.0.0`

## Architecture

```mermaid
graph TD
    %% ==================== Entry Point ====================
    subgraph Entry["Entry Point"]
        main_py["main.py"]
        main_fn["main()"]
        load_stylesheet["load_stylesheet()"]
    end

    main_py --> main_fn
    main_fn --> load_stylesheet

    %% ==================== Configuration ====================
    subgraph Config["config.py"]
        cfg_const["Constants:<br/>APP_VERSION, APP_ID<br/>OLLAMA_HOST, OLLAMA_MODEL<br/>TARGET_IMAGE_SIZE<br/>INFERENCE_PARAMS, PROMPTS"]
    end

    %% ==================== Language Handler ====================
    subgraph LangHandler["lang_handler.py"]
        get_default_language["get_default_language()"]
        get_available_languages["get_available_languages()"]
        load_language["load_language()"]
    end

    %% ==================== File Handler ====================
    subgraph FileHandler["file_handler.py"]
        pad_image["pad_image()"]
        preprocess_image["preprocess_image()"]
        get_image_bytes["get_image_bytes()"]
        get_pdf_page_count["get_pdf_page_count()"]
        extract_pdf_page_bytes["extract_pdf_page_bytes()"]
    end

    preprocess_image --> pad_image
    get_image_bytes --> preprocess_image
    extract_pdf_page_bytes --> preprocess_image
    pad_image -.-> cfg_const

    %% ==================== Ollama Service ====================
    subgraph OllamaService["ollama_service.py"]
        stream_ocr_response["stream_ocr_response()"]
        
        subgraph ModelUnloadWorkerClass["class ModelUnloadWorker(QThread)"]
            muw_init["__init__()"]
            muw_run["run()"]
            muw_signal["Signal: finished"]
        end
    end

    muw_run -.-> cfg_const

    %% ==================== OCR Worker ====================
    subgraph OCRWorkerModule["ocr_worker.py"]
        subgraph OCRWorkerClass["class OCRWorker(QThread)"]
            ocr_init["__init__()"]
            ocr_run["run()"]
            ocr_process_chunk["process_chunk()"]
            ocr_stop["stop()"]
            ocr_signals["Signals:<br/>stream_chunk, image_started<br/>image_finished, box_detected<br/>finished_all, error_occurred"]
        end
    end

    ocr_run --> stream_ocr_response
    ocr_run --> get_image_bytes
    ocr_run --> extract_pdf_page_bytes
    ocr_run --> ocr_process_chunk
    ocr_run -.-> cfg_const

    %% ==================== Windows Taskbar ====================
    subgraph WinTaskbar["win_taskbar.py"]
        subgraph GUIDClass["class GUID(Structure)"]
            guid_init["__init__()"]
        end
        
        subgraph ITaskbarList3Class["class ITaskbarList3(Structure)"]
        end
        
        subgraph ITaskbarList3VtblClass["class ITaskbarList3Vtbl(Structure)"]
            vtbl_fields["SetProgressValue()<br/>SetProgressState()"]
        end
        
        subgraph TaskbarProgressClass["class TaskbarProgress"]
            tbp_init["__init__()"]
            tbp_init_com["_init_com()"]
            tbp_set_progress["set_progress()"]
            tbp_stop_progress["stop_progress()"]
        end
    end

    tbp_init --> tbp_init_com
    tbp_init_com --> guid_init
    tbp_set_progress --> vtbl_fields
    tbp_stop_progress --> vtbl_fields

    %% ==================== UI: Main Window ====================
    subgraph MainWindowModule["ui/main_window.py"]
        subgraph MainWindowClass["class MainWindow(QMainWindow)"]
            mw_init["__init__()"]
            mw_showEvent["showEvent()"]
            mw_force_gl_init["force_gl_init()"]
            mw_init_ui["init_ui()"]
            mw_show_about["show_about()"]
            mw_unload_model["unload_model()"]
            mw_on_unload_finished["on_unload_finished()"]
            mw_change_language["change_language()"]
            mw_apply_language["apply_language()"]
            mw_set_processing_state["set_processing_state()"]
            mw_initiate_processing["initiate_processing()"]
            mw_start_processing["start_processing()"]
            mw_stop_processing["stop_processing()"]
            mw_on_image_started["on_image_started()"]
            mw_on_image_finished["on_image_finished()"]
            mw_on_finished["on_finished()"]
        end
    end

    mw_init --> mw_init_ui
    mw_showEvent --> mw_force_gl_init
    mw_init_ui --> ControlPanelClass
    mw_init_ui --> OutputPanelClass
    mw_init --> mw_apply_language
    mw_apply_language --> load_language
    mw_change_language --> mw_apply_language
    mw_unload_model --> ModelUnloadWorkerClass
    mw_on_unload_finished -.-> muw_signal
    mw_initiate_processing --> mw_start_processing
    mw_start_processing --> OCRWorkerClass
    mw_start_processing --> mw_set_processing_state
    mw_stop_processing --> ocr_stop
    mw_on_image_started --> tbp_set_progress
    mw_on_finished --> tbp_stop_progress

    %% ==================== UI: Control Panel ====================
    subgraph ControlPanelModule["ui/control_panel.py"]
        subgraph ControlPanelClass["class ControlPanel(QWidget)"]
            cp_init["__init__()"]
            cp_update_language["update_language()"]
            cp_update_status["update_status()"]
            cp_set_processing_state["set_processing_state()"]
            cp_add_images["add_images()"]
            cp_add_pdf["add_pdf()"]
            cp_clear_queue["clear_queue()"]
            cp_on_queue_item_changed["on_queue_item_changed()"]
            cp_perform_load_image["_perform_load_image()"]
            cp_on_image_loaded["on_image_loaded()"]
            cp_on_start_click["on_start_click()"]
            cp_on_stop_click["on_stop_click()"]
            cp_on_process_started["on_process_started()"]
            cp_on_stream_chunk["on_stream_chunk()"]
            cp_draw_box["draw_box()"]
            cp_increment_progress["increment_progress()"]
            cp_signals["Signals:<br/>start_requested<br/>stop_requested"]
        end
    end

    cp_init --> ImageViewerClass
    cp_add_pdf --> get_pdf_page_count
    cp_add_pdf --> PageRangeDialogClass
    cp_on_queue_item_changed --> cp_perform_load_image
    cp_perform_load_image --> ImageLoaderClass
    cp_on_image_loaded --> iv_display_image
    cp_on_process_started --> iv_display_image
    cp_draw_box --> iv_draw_box

    %% ==================== UI: Output Panel ====================
    subgraph OutputPanelModule["ui/output_panel.py"]
        balance_latex["balance_latex_delimiters()"]
        
        subgraph FancyOutputClass["class FancyOutput(QWebEngineView)"]
            fo_init["__init__()"]
            fo_set_markdown["set_markdown()"]
            fo_copy_content["copy_content()"]
            fo_contextMenuEvent["contextMenuEvent()"]
        end
        
        subgraph OutputPanelClass["class OutputPanel(QWidget)"]
            op_init["__init__()"]
            op_update_language["update_language()"]
            op_update_copy_button["_update_copy_button_text()"]
            op_append_text["append_text()"]
            op_render_fancy["render_fancy_output()"]
            op_clear["clear()"]
            op_copy_output["copy_output()"]
        end
    end

    op_init --> FancyOutputClass
    op_render_fancy --> fo_set_markdown
    fo_set_markdown --> balance_latex

    %% ==================== UI: Image Viewer ====================
    subgraph ImageViewerModule["ui/image_viewer.py"]
        subgraph ImageViewerClass["class ImageViewer(QGraphicsView)"]
            iv_init["__init__()"]
            iv_display_image["display_image()"]
            iv_draw_box["draw_box()"]
            iv_fit_content["fit_content()"]
            iv_resizeEvent["resizeEvent()"]
        end
    end

    iv_display_image --> iv_fit_content
    iv_resizeEvent --> iv_fit_content

    %% ==================== UI: Image Loader ====================
    subgraph ImageLoaderModule["ui/image_loader.py"]
        subgraph ImageLoaderClass["class ImageLoaderThread(QThread)"]
            il_init["__init__()"]
            il_run["run()"]
            il_cancel["cancel()"]
            il_signals["Signals:<br/>image_loaded<br/>error_occurred"]
        end
    end

    il_run --> get_image_bytes
    il_run --> extract_pdf_page_bytes

    %% ==================== UI: Dialogs ====================
    subgraph DialogsModule["ui/dialogs.py"]
        subgraph PageRangeDialogClass["class PageRangeDialog(QDialog)"]
            prd_init["__init__()"]
            prd_validate["validate_and_accept()"]
            prd_get_range["get_range()"]
        end
    end

    %% ==================== Main Entry Connections ====================
    main_fn --> MainWindowClass
    main_fn -.-> cfg_const
```

## Environment setup

### Automated
- Execute `env_setup.cmd`.

### Manual
1. **Python:**
   - Download [Python 3.13.9 Embeddable (Windows x64)](https://www.python.org/ftp/python/3.13.9/python-3.13.9-embed-amd64.zip).
   - Extract to `python/`.
   - Edit `python/python313._pth`: Uncomment line 5: `import site`.

2. **pip + requirements:**
   - Download [get-pip.py](https://bootstrap.pypa.io/get-pip.py).
     ```powershell
     .\python\python.exe get-pip.py
     .\python\python.exe -m pip install -r requirements.txt
     ```

3. **Ollama:**
   - Download [ollama-windows-amd64.zip](https://ollama.com/download/ollama-windows-amd64.zip).
   - Extract to `ollama/`.

4. **DeepSeek-OCR Model:**
   ```powershell
   $env:OLLAMA_HOST = "127.0.0.1:11435" # Avoid port conflict
   $env:OLLAMA_MODELS = Join-Path $PSScriptRoot "models"
   .\ollama\ollama.exe pull deepseek-ocr:3b
   ```

## Running
- **With GPU (If possible):** `run.cmd`
- **With GPU (+ Logging):** `run_wlog.cmd`
- **CPU-Only Mode:** `run_cpu-only.cmd`
- **CPU-Only Mode (+ Logging):** `run_cpu-only_wlog.cmd`

## Packaging
- Execute `make_release.cmd` to create release zip.

## Debloating `src/res/node/mathjax` and `src/res/node/@mathjax/mathjax-newcm-font`
```
./core.js
./loader.js
./startup.js
./mml-chtml-nofont.js
./mml-chtml.js
./mml-svg-nofont.js
./mml-svg.js
./tex-chtml-nofont.js
./tex-chtml.js
./tex-mml-chtml-nofont.js
./tex-mml-chtml.js
./tex-mml-svg-nofont.js
./tex-svg-nofont.js
./tex-svg.js
./input/asciimath.js
./input/mml.js
./input/tex.js
./input/tex-base.js
./input/mml/
./output/
./ui/
./chtml/
./examples/
```
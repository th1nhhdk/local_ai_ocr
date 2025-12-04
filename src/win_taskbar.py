# src/win_taskbar.py
# Windows-specific feature: Shows progress bar on the app's taskbar icon.
# Uses COM (Component Object Model) to interact with Windows Shell APIs.

import ctypes
from ctypes import wintypes, POINTER, Structure, c_ulong, c_void_p, HRESULT

# GUIDs (globally unique identifiers) for Windows COM interfaces
# These are fixed IDs defined by Microsoft to access taskbar features
CLSID_TaskbarList = "{56FDF344-FD6D-11d0-958A-006097C9A090}"
IID_ITaskbarList3 = "{EA1AFB91-9E28-4B86-90E9-9E9F8A5EEFAF}"

# Progress bar states - these control the color/behavior of the taskbar icon
TBPF_NOPROGRESS = 0x00  # No progress indicator
TBPF_INDETERMINATE = 0x01 # Spinner/pulsing animation
TBPF_NORMAL = 0x02  # Green progress bar
TBPF_ERROR = 0x04 # Red error state
TBPF_PAUSED = 0x08 # Yellow paused state


# ==================== COM Structure Definitions ====================
# These mirror Windows C++ structures in Python for interop

class GUID(Structure):
    # 128-bit globally unique identifier structure.
    # Used to identify COM interfaces and classes.
    _fields_ = [
        ('Data1', c_ulong),
        ('Data2', ctypes.c_ushort),
        ('Data3', ctypes.c_ushort),
        ('Data4', ctypes.c_ubyte * 8)
    ]
    def __init__(self, guid_str):
        from uuid import UUID
        u = UUID(guid_str)
        # Split UUID into Windows GUID format components
        self.Data1 = u.time_low
        self.Data2 = u.time_mid
        self.Data3 = u.time_hi_version
        self.Data4 = (ctypes.c_ubyte * 8)(*u.bytes[8:])

class ITaskbarList3(Structure):
    # Forward declaration for the COM interface pointer.
    pass

class ITaskbarList3Vtbl(Structure):
    """
    Virtual function table (vtable) for ITaskbarList3.

    In COM, objects expose their methods through vtables - arrays of
    function pointers. This structure mirrors the C++ vtable layout
    so we can call Windows API methods from Python.

    Methods are inherited through the interface hierarchy:
    IUnknown -> ITaskbarList -> ITaskbarList2 -> ITaskbarList3
    """
    _fields_ = [
        # IUnknown methods (base COM interface)
        ('QueryInterface', c_void_p),
        ('AddRef', c_void_p),
        ('Release', c_void_p),
        # ITaskbarList methods
        ('HrInit', c_void_p),
        ('AddTab', c_void_p),
        ('DeleteTab', c_void_p),
        ('ActivateTab', c_void_p),
        ('SetActiveAlt', c_void_p),
        # ITaskbarList2 methods
        ('MarkFullscreenWindow', c_void_p),
        # ITaskbarList3 methods - these are what we actually use
        ('SetProgressValue', ctypes.WINFUNCTYPE(HRESULT, POINTER(ITaskbarList3), wintypes.HWND, ctypes.c_ulonglong, ctypes.c_ulonglong)),
        ('SetProgressState', ctypes.WINFUNCTYPE(HRESULT, POINTER(ITaskbarList3), wintypes.HWND, ctypes.c_int)),
    ]

# Complete the forward declaration by assigning vtable pointer field
ITaskbarList3._fields_ = [('lpVtbl', POINTER(ITaskbarList3Vtbl))]


class TaskbarProgress:
    # High-level wrapper for Windows taskbar progress API.
    def __init__(self):
        self._taskbar = None
        self._initialized = False
        try:
            self._init_com()
        except Exception as e:
            print(f"Warning: Failed to init taskbar progress: {e}")

    def _init_com(self):
        # Initialize COM library and create TaskbarList object.
        # CoInitialize: Required before using any COM functions
        try:
            ctypes.windll.ole32.CoInitialize(None)
        except:
            pass  # Might already be initialized by Qt

        clsid = GUID(CLSID_TaskbarList)
        iid = GUID(IID_ITaskbarList3)

        self._taskbar = POINTER(ITaskbarList3)()

        # CoCreateInstance: Creates a COM object and returns interface pointer
        # Parameters: class ID, outer object (for aggregation), context, interface ID, output pointer
        res = ctypes.windll.ole32.CoCreateInstance(
            ctypes.byref(clsid),
            None,
            1,  # CLSCTX_INPROC_SERVER = load as in-process DLL
            ctypes.byref(iid),
            ctypes.byref(self._taskbar)
        )

        if res == 0:  # S_OK = success
            self._initialized = True

    def set_progress(self, hwnd, current, total):
        # Set the taskbar progress bar.
        if not self._initialized or not self._taskbar: return
        try:
            # Navigate: pointer -> contents -> vtable pointer -> vtable -> method
            self._taskbar.contents.lpVtbl.contents.SetProgressState(self._taskbar, hwnd, TBPF_NORMAL)
            self._taskbar.contents.lpVtbl.contents.SetProgressValue(self._taskbar, hwnd, current, total)
        except Exception:
            pass

    def stop_progress(self, hwnd):
        # Remove the progress bar from taskbar icon.
        if not self._initialized or not self._taskbar: return
        try:
            self._taskbar.contents.lpVtbl.contents.SetProgressState(self._taskbar, hwnd, TBPF_NOPROGRESS)
        except Exception:
            pass

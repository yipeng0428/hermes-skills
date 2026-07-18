# OpenCL / CUDA Runtime Component Gaps in NVIDIA Drivers

## Session Reference: 2026-07-14

### Environment
- GPU: NVIDIA GeForce GTX 1050 Ti (4GB) on Windows 10 Enterprise (Build 19045)
- Driver: 32.0.15.6094 (560.94) — appeared up-to-date
- Symptom: User reported OpenCL was "not installed"; games/apps reported "No OpenCL platforms"

### Diagnosis

**Hardware check (bash via MSYS):**
```bash
wmic path win32_VideoController get Name, AdapterRAM, DriverVersion
# → GeForce GTX 1050 Ti, 4293918720 bytes, 32.0.15.6094
```

**CUDA Toolkit check:**
```bash
nvcc --version → nvcc not found
ls /c/Program\ Files/NVIDIA\ GPU\ Computing\ Toolkit/ → directory missing
# → CUDA toolkit not installed (expected — separate from OpenCL runtime)
```

**OpenCL ICD Registry Check:**
```bash
reg query "HKLM\SOFTWARE\Khronos\OpenCL\Vendors"         → key missing
reg query "HKLM\SOFTWARE\Wow6432Node\Khronos\OpenCL\Vendors" → key missing
# → NVIDIA's OpenCL ICD was never installed
```

**nvopencl.dll check (the actual driver-side ICD):**
```bash
ls /c/Windows/System32/nvopencl.dll   → NOT found
ls /c/Windows/SysWOW64/nvopencl.dll   → NOT found
# → NVIDIA driver binary is missing the ICD component
```

**clinfo check:**
```bash
where clinfo → clinfo not found
# clinfo is a third-party tool not bundled with NVIDIA drivers
```

### Conclusion

The Microsoft ICD loader (`C:\Windows\System32\OpenCL.dll`) was present at version 1.0 — it only dispatches to vendor ICDs listed in the registry. Since NVIDIA's registry entries and `nvopencl.dll` were both absent, **no OpenCL platform was available** despite a non-trivial driver version.

Root cause: The NVIDIA driver package installed was a "driver-only" or upgrade-install skippable variant that didn't include the OpenCL ICD components. Common when:
- User installed via Windows Update minimal driver
- Previous driver upgrade used "Express install" which may skip optional components
- Driver was extracted/installed via third-party tools (e.g., Display Driver Uninstaller remnants)

### Fix Applied

Clean install from NVIDIA website:
1. Download from https://www.nvidia.cn/Download/index.aspx — select GeForce / 10 Series / GTX 1050 Ti / Windows 10 64-bit
2. Run installer → **Custom (Advanced)** → **☑ Perform clean installation**
3. Reboot

After this, registry keys appear and `nvopencl.dll` is present → OpenCL works.

### Pro forma Notes

1. Never conclude "OpenCL is installed" merely because `System32\OpenCL.dll` exists — that's only the Microsoft dispatcher, not the vendor ICD
2. For games/apps, check both `HKLM\SOFTWARE\Khronos\OpenCL\Vendors` (64-bit) and `HKLM\SOFTWARE\Wow6432Node\...\Vendors` (32-bit apps)
3. `clinfo` must be installed separately — not bundled with NVIDIA drivers. Useful for verification but not required for runtime
4. CUDA Toolkit is NOT required for OpenCL; they're separate runtime systems. Only needed for development or CUDA-specific compute apps
5. Same pattern applies to Vulkan: `vulkan-1.dll` in System32 needs `nvoglv64.dll` (for NVIDIA) plus registry entries in `HKLM\SOFTWARE\Khronos\Vulkan\Drivers`

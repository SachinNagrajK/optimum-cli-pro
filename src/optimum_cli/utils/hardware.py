"""Hardware detection utilities."""

import platform
import psutil
from typing import Dict, Any, Optional

from optimum_cli.utils.logger import log
from optimum_cli.utils.exceptions import HardwareDetectionError


class HardwareDetector:
    """Hardware detection and capability checking."""
    
    def __init__(self):
        self._cpu_info: Optional[Dict[str, Any]] = None
        self._gpu_info: Optional[Dict[str, Any]] = None
    
    def detect_all(self) -> Dict[str, Any]:
        """Detect all hardware information."""
        try:
            return {
                "cpu": self.detect_cpu(),
                "memory": self.detect_memory(),
                "gpu": self.detect_gpu(),
                "platform": self.detect_platform(),
            }
        except Exception as e:
            log.error(f"Hardware detection failed: {e}")
            raise HardwareDetectionError(f"Failed to detect hardware: {e}")
    
    def detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information."""
        if self._cpu_info is not None:
            return self._cpu_info
        
        try:
            cpu_info = {
                "brand": platform.processor(),
                "architecture": platform.machine(),
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                "vendor": self._detect_cpu_vendor(),
                "features": self._detect_cpu_features(),
            }
            self._cpu_info = cpu_info
            return cpu_info
        except Exception as e:
            log.warning(f"CPU detection failed: {e}")
            return {"error": str(e)}
    
    def detect_memory(self) -> Dict[str, Any]:
        """Detect memory information."""
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent_used": mem.percent,
            }
        except Exception as e:
            log.warning(f"Memory detection failed: {e}")
            return {"error": str(e)}
    
    def detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU information."""
        if self._gpu_info is not None:
            return self._gpu_info
        
        gpu_info = {"available": False, "devices": []}
        
        # Try to detect CUDA
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info["available"] = True
                gpu_info["backend"] = "cuda"
                gpu_info["device_count"] = torch.cuda.device_count()
                gpu_info["devices"] = [
                    {
                        "id": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory_gb": round(
                            torch.cuda.get_device_properties(i).total_memory / (1024**3), 2
                        ),
                    }
                    for i in range(torch.cuda.device_count())
                ]
        except (ImportError, Exception) as e:
            log.debug(f"CUDA detection failed: {e}")
        
        self._gpu_info = gpu_info
        return gpu_info
    
    def detect_platform(self) -> Dict[str, Any]:
        """Detect platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "python_version": platform.python_version(),
        }
    
    def _detect_cpu_vendor(self) -> str:
        """Detect CPU vendor."""
        try:
            processor = platform.processor().lower()
            if "intel" in processor:
                return "intel"
            elif "amd" in processor:
                return "amd"
            elif "arm" in processor or "apple" in processor:
                return "arm"
            else:
                return "unknown"
        except Exception:
            return "unknown"
    
    def _detect_cpu_features(self) -> Dict[str, bool]:
        """Detect CPU features (AVX, AVX2, AVX-512, etc.)."""
        features = {
            "avx": False,
            "avx2": False,
            "avx512": False,
            "sse4_2": False,
        }
        
        try:
            # On Windows, we can check via platform
            if platform.system() == "Windows":
                # Limited feature detection on Windows without external tools
                pass
            # On Linux, we could read /proc/cpuinfo
            elif platform.system() == "Linux":
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        cpuinfo = f.read()
                        if "avx512" in cpuinfo:
                            features["avx512"] = True
                        if "avx2" in cpuinfo:
                            features["avx2"] = True
                        if "avx" in cpuinfo:
                            features["avx"] = True
                        if "sse4_2" in cpuinfo:
                            features["sse4_2"] = True
                except Exception:
                    pass
        except Exception as e:
            log.debug(f"CPU feature detection failed: {e}")
        
        return features
    
    def recommend_backend(self, check_availability: bool = True) -> str:
        """
        Recommend best backend based on hardware.
        
        Args:
            check_availability: If True, only recommend installed backends
        
        Returns:
            Backend name
        """
        hardware = self.detect_all()
        
        # Determine ideal backend based on hardware
        ideal_backend = None
        
        # GPU available - prefer BetterTransformer
        if hardware["gpu"]["available"]:
            ideal_backend = "bettertransformer"
            log.info("GPU detected, ideal backend: BetterTransformer")
        # Intel CPU - prefer OpenVINO
        elif hardware["cpu"].get("vendor", "unknown") == "intel":
            ideal_backend = "openvino"
            log.info("Intel CPU detected, ideal backend: OpenVINO")
        # Default to ONNX for cross-platform compatibility
        else:
            ideal_backend = "onnx"
            log.info("Default backend: ONNX Runtime")
        
        # If checking availability, verify backend is installed
        if check_availability:
            try:
                from optimum_cli.core.backend_manager import get_backend_manager
                manager = get_backend_manager()
                
                # Check if ideal backend is available
                try:
                    backend = manager.backends.get(ideal_backend)
                    if backend and backend.validate_environment():
                        log.info(f"Recommended backend '{ideal_backend}' is available")
                        return ideal_backend
                except Exception:
                    pass
                
                # Fallback: find first available backend
                log.warning(f"Ideal backend '{ideal_backend}' not available, finding fallback...")
                for fallback in ["onnx", "bettertransformer", "openvino"]:
                    try:
                        backend = manager.backends.get(fallback)
                        if backend and backend.validate_environment():
                            log.info(f"Using fallback backend: {fallback}")
                            return fallback
                    except Exception:
                        continue
                
                # No backends available
                log.warning(f"No backends available, recommending {ideal_backend} (needs installation)")
                return ideal_backend
                
            except Exception as e:
                log.debug(f"Could not check backend availability: {e}")
                return ideal_backend
        
        return ideal_backend
    
    def get_optimal_threads(self) -> int:
        """Get optimal number of threads for CPU operations."""
        try:
            physical_cores = psutil.cpu_count(logical=False)
            return physical_cores if physical_cores else 1
        except Exception:
            return 1


# Global hardware detector instance
_detector: Optional[HardwareDetector] = None


def get_hardware_detector() -> HardwareDetector:
    """Get global hardware detector instance."""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector

import time
import psutil
import asyncio
import logging
from collections import deque
from typing import Dict, Any, List, Optional

logger = logging.getLogger("phantom_hand")

class PerformanceMonitor:
    """
    PHANTOM HAND Performance Kernel.
    Monitors system health, vision pipeline latency, and tracking stability.
    Provides telemetry for the JARVIS-style HUD.
    """
    def __init__(self):
        # Sliding windows for smooth metrics
        self._fps_window = deque(maxlen=60)
        self._latencies: Dict[str, deque] = {
            "tracking": deque(maxlen=60),
            "gesture": deque(maxlen=60),
            "composition": deque(maxlen=60),
            "total": deque(maxlen=60)
        }
        
        self.last_frame_time = time.perf_counter()
        self._cached_cpu = 0.0
        self._cached_mem = 0.0
        self._last_sys_check = 0.0
        
        # Stability metrics
        self._confidence_window = deque(maxlen=30)
        self.start_time = time.time()

    def record_frame(self, 
                    tracking_ms: float, 
                    gesture_ms: float, 
                    comp_ms: float, 
                    confidence: float = 1.0):
        """Records metrics for a single vision pipeline iteration."""
        now = time.perf_counter()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if dt > 0:
            self._fps_window.append(1.0 / dt)

        self._latencies["tracking"].append(tracking_ms)
        self._latencies["gesture"].append(gesture_ms)
        self._latencies["composition"].append(comp_ms)
        self._latencies["total"].append(tracking_ms + gesture_ms + comp_ms)
        self._confidence_window.append(confidence)

        self._check_system_health()

    def _check_system_health(self):
        """Throttled check for CPU/MEM to minimize overhead."""
        now = time.perf_counter()
        if now - self._last_sys_check > 1.0:
            process = psutil.Process()
            self._cached_mem = process.memory_info().rss / (1024 * 1024)
            self._cached_cpu = psutil.cpu_percent(interval=None)
            self._last_sys_check = now
            
            # Log critical alerts
            if self._cached_cpu > 90:
                logger.warning(f"SYSTEM_ALERT: CRITICAL_CPU_USAGE [{self._cached_cpu}%]")
            if self._cached_mem > 1024:
                logger.warning(f"SYSTEM_ALERT: HIGH_MEMORY_USAGE [{self._cached_mem:.1f} MB]")

    def get_heartbeat(self) -> Dict[str, Any]:
        """Generates a comprehensive telemetry packet for the HUD."""
        def avg(window: deque) -> float:
            return sum(window) / len(window) if window else 0.0

        return {
            "status": "OPERATIONAL",
            "uptime": int(time.time() - self.start_time),
            "telemetry": {
                "fps": round(avg(self._fps_window), 1),
                "cpu": round(self._cached_cpu, 1),
                "memory_mb": round(self._cached_mem, 1)
            },
            "latency_ms": {
                "tracking": round(avg(self._latencies["tracking"]), 2),
                "gesture": round(avg(self._latencies["gesture"]), 2),
                "composition": round(avg(self._latencies["composition"]), 2),
                "total": round(avg(self._latencies["total"]), 2)
            },
            "stability": {
                "signal_quality": round(avg(self._confidence_window) * 100, 1),
                "jitter_index": round(1.0 / (avg(self._fps_window) + 0.1), 3)
            }
        }

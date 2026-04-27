import time
import psutil
import asyncio
from collections import deque
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, sio=None, event_loop=None):
        self.sio = sio
        self.event_loop = event_loop
        self._fps_window = deque(maxlen=60)
        self._track_lat_window = deque(maxlen=60)
        self._gest_lat_window = deque(maxlen=60)
        self._sock_lat_window = deque(maxlen=60)

        self.last_frame_time = time.time()
        self.consecutive_low_fps_start = None
        self._cached_cpu = 0.0
        self._cached_mem = 0.0
        self._last_sys_check = 0.0

    def mark_frame(self, tracking_ms: float, gesture_ms: float, socket_ms: float):
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if dt > 0:
            self._fps_window.append(1.0 / dt)

        self._track_lat_window.append(tracking_ms)
        self._gest_lat_window.append(gesture_ms)
        self._sock_lat_window.append(socket_ms)

        self._check_alerts()

    @property
    def fps(self) -> float:
        return sum(self._fps_window) / len(self._fps_window) if self._fps_window else 0.0

    @property
    def avg_tracking_latency_ms(self) -> float:
        return sum(self._track_lat_window) / len(self._track_lat_window) if self._track_lat_window else 0.0

    @property
    def avg_gesture_latency_ms(self) -> float:
        return sum(self._gest_lat_window) / len(self._gest_lat_window) if self._gest_lat_window else 0.0

    def _update_sys_stats(self):
        now = time.time()
        if now - self._last_sys_check > 1.0:
            # psutil calls can be blocking/heavy, only do it once per second
            process = psutil.Process()
            self._cached_mem = process.memory_info().rss / (1024 * 1024)
            self._cached_cpu = psutil.cpu_percent(interval=None)
            self._last_sys_check = now

    @property
    def memory_mb(self) -> float:
        self._update_sys_stats()
        return self._cached_mem

    @property
    def cpu_percent(self) -> float:
        self._update_sys_stats()
        return self._cached_cpu

    def report(self) -> dict:
        return {
            "fps": round(self.fps, 1),
            "tracking_latency_ms": round(self.avg_tracking_latency_ms, 2),
            "gesture_latency_ms": round(self.avg_gesture_latency_ms, 2),
            "socket_latency_ms": round(sum(self._sock_lat_window) / len(self._sock_lat_window) if self._sock_lat_window else 0.0, 2),
            "memory_mb": round(self.memory_mb, 1),
            "cpu_percent": round(self.cpu_percent, 1)
        }

    def _check_alerts(self):
        now = time.time()
        alerts = []

        # 1. FPS check (<20 for 2 seconds)
        if self.fps > 0 and self.fps < 20:
            if self.consecutive_low_fps_start is None:
                self.consecutive_low_fps_start = now
            elif now - self.consecutive_low_fps_start >= 2.0:
                alerts.append(f"FPS dropped below 20 ({round(self.fps,1)})")
        else:
            self.consecutive_low_fps_start = None

        # 2. Memory check (> 800MB)
        if self.memory_mb > 800:
            alerts.append(f"High memory usage: {self.memory_mb:.1f} MB")

        # 3. CPU check (> 85%)
        if self.cpu_percent > 85:
            alerts.append(f"High CPU usage: {self.cpu_percent:.1f}%")

        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT: {alert}")
            if self.sio and self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.sio.emit("performance_alert", {"alert": alert, "timestamp": now}),
                    self.event_loop
                )

with open('backend/core/hand_tracker.py', 'r') as f:
    content = f.read()

content = content.replace(
    "timestamp = int(time.perf_counter() * 1000)",
    "timestamp = int(time.perf_counter() * 1000)\n        if hasattr(self, '_last_timestamp') and timestamp <= self._last_timestamp:\n            timestamp = self._last_timestamp + 1\n        self._last_timestamp = timestamp"
)

with open('backend/core/hand_tracker.py', 'w') as f:
    f.write(content)

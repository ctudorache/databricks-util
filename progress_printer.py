import time, datetime

class ProgressPrinter:
    def __init__(self, max_value, progress_step = 0.01):
        self.max_value = max_value
        self.crt_value = 0
        self.progress_step = progress_step
        self.last_progress = None
        self.start_ts = time.time()

    def set(self, value):
        self.crt_value = value
        p = self.crt_value / self.max_value
        if not self.last_progress or p > self.last_progress + self.progress_step:
            remaining = "unknown"
            if p > 0:
                duration_sec = time.time() - self.start_ts
                total_sec = duration_sec / p if p > 0 else 0
                remaining_sec = total_sec - duration_sec
                remaining = str(datetime.timedelta(seconds=remaining_sec))
            print(f"progress: {self.crt_value}/{self.max_value} ({p:.1%}), remaining time: {remaining}")
            self.last_progress = p

    def inc(self, count=1):
        self.set(self.crt_value + count)

class ProgressCounter:
    def __init__(self, max_value):
        self.max_value = max_value
        self.crt_value = 0
        self.start_ts = time.time()

    def __str__(self):
        p = self.crt_value / self.max_value

        duration_sec = time.time() - self.start_ts
        took = str(datetime.timedelta(seconds=duration_sec))

        remaining = "unknown"
        if p > 0:
            total_sec = duration_sec / p if p > 0 else 0
            remaining_sec = total_sec - duration_sec
            remaining = str(datetime.timedelta(seconds=remaining_sec))
        return f"{self.crt_value}/{self.max_value} ({p:.1%}), took: {took}, remaining time: {remaining}"

    def inc(self, count=1):
        self.crt_value += count
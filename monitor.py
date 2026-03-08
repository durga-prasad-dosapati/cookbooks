import psutil

class ResourceMonitor:
    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage."""
        return psutil.cpu_percent(interval=0.5)

    @staticmethod
    def get_ram_usage():
        """Returns the current RAM usage percentage."""
        return psutil.virtual_memory().percent

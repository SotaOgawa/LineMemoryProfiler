import functools
import linecache
import sys
import threading
import psutil

try:
    from pynvml import (
        nvmlInit,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
    )

    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    pynvml_available = True
except Exception:
    pynvml_available = False


def memory_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        memory_logs = []
        lock = threading.Lock()

        # 前回のメモリ使用量を保持
        previous_cpu_mem = 0
        previous_gpu_mem = 0
        previous_code = ""
        previous_line_no = 0

        def local_tracer(frame, event, arg):
            if event == 'line':
                nonlocal previous_code
                nonlocal previous_cpu_mem
                nonlocal previous_gpu_mem
                nonlocal previous_line_no
                
                lineno = frame.f_lineno
                code = linecache.getline(frame.f_code.co_filename, lineno).strip()

                # CPUメモリ使用量を取得
                process = psutil.Process()
                cpu_mem = process.memory_info().rss / 1024 / 1024  # MB単位
                cpu_diff = cpu_mem - previous_cpu_mem
                previous_cpu_mem = cpu_mem

                # GPUメモリ使用量を取得
                if pynvml_available:
                    mem_info = nvmlDeviceGetMemoryInfo(handle)
                    gpu_mem = mem_info.used / 1024 / 1024  # MB単位
                    gpu_diff = gpu_mem - previous_gpu_mem
                    previous_gpu_mem = gpu_mem
                else:
                    gpu_mem = None
                    gpu_diff = None

                with lock:
                    memory_logs.append(
                        (previous_line_no, previous_code, cpu_mem, cpu_diff, gpu_mem, gpu_diff)
                    )
                
                previous_code = code
                previous_line_no = lineno
            return local_tracer

        def global_tracer(frame, event, arg):
            if event == 'call' and frame.f_code == func.__code__:
                # デコレータをつけた関数に入った場合、ローカルトレース関数を返す
                return local_tracer
            else:
                # それ以外の場合はトレースしない
                return None

        # トレースを開始
        sys.settrace(global_tracer)
        try:
            result = func(*args, **kwargs)
        finally:
            # トレースを停止
            sys.settrace(None)
            
            # 最後の行の実行結果を出力
            
            # CPUメモリ使用量を取得
            process = psutil.Process()
            cpu_mem = process.memory_info().rss / 1024 / 1024  # MB単位
            cpu_diff = cpu_mem - previous_cpu_mem
            previous_cpu_mem = cpu_mem
            # GPUメモリ使用量を取得
            if pynvml_available:
                mem_info = nvmlDeviceGetMemoryInfo(handle)
                gpu_mem = mem_info.used / 1024 / 1024  # MB単位
                gpu_diff = gpu_mem - previous_gpu_mem
                previous_gpu_mem = gpu_mem
            else:
                gpu_mem = None
                gpu_diff = None
                
            with lock:
                memory_logs.append(
                    (previous_line_no, previous_code, cpu_mem, cpu_diff, gpu_mem, gpu_diff)
                )
            
            # ログの出力
            print(f"Function '{func.__name__}' memory usage per line:")
            for log in memory_logs:
                lineno, code, cpu_mem, cpu_diff, gpu_mem, gpu_diff = log
                mem_info = f"Line {lineno}: CPU {cpu_mem:.2f} MB ({cpu_diff:+.2f} MB)"
                if gpu_mem is not None:
                    mem_info += f", GPU {gpu_mem:.2f} MB ({gpu_diff:+.2f} MB)"
                print(f"{mem_info} | {code}")
        return result

    return wrapper

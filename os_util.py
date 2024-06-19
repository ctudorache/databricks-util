import os
import subprocess
  
def os_exec(*args):
  print(f"exec: {args}")
  s = subprocess.run(args, check=True, capture_output=True, encoding='ascii')
  print(f"Code: {s.returncode}")
  print("Error: " + s.stderr)
  print("Output: " + s.stdout)

def posix_path(p):
  if p.startswith('dbfs:/'):
    return f'/dbfs/{p[6:]}'
  return p

def run_os_util_tests():
    print(f"Test: os_exec: ls -la")
    os_exec("ls", "-la")


import subprocess
from load_config import get_config_yaml
enviroment_path = get_config_yaml('requirements')
# Đọc tệp văn bản
with open(enviroment_path, 'r') as file:
    lines = file.readlines()

# Lặp qua từng dòng lệnh và chạy nó trong terminal
for line in lines:
    subprocess.run(line, shell=True)

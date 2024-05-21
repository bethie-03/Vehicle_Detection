import subprocess
import setuptools

from load_config import get_config_yaml
enviroment_path = get_config_yaml('requirements')
# Đọc tệp văn bản
with open(enviroment_path, 'r') as file:
    lines = file.readlines()

# Lặp qua từng dòng lệnh và chạy nó trong terminal
for line in lines:
    subprocess.run(line, shell=True)

# def set_up():
#     setuptools.setup(
#         name="chaos",  
#         version="0.0.1",
#         packages=setuptools.find_packages(),
#         python_requires='>=3.6',
#         entry_points={
#             "console_scripts": [
#                 "chaos=chaos.main:get_CLI",  
#             ]
#         },
#     )

# set_up()
import yaml
import ast
import os

def get_absolute_path(filename):
    dir_path = os.path.dirname(__file__)
    absolute_path = os.path.join(dir_path, filename)
    return absolute_path


def get_config_yaml(keywords):
    config = get_absolute_path(r'config.yaml')
    print(config)
    with open(config, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        requirements_path = config.get(keywords, '')
        return requirements_path

def string_to_list(keywords):
# Loại bỏ các ký tự không cần thiết
    cleaned_string = keywords.strip("[]")

    # Tách chuỗi thành các phần tử của danh sách
    # Sử dụng ast.literal_eval để an toàn chuyển đổi chuỗi thành danh sách
    list_of_classes = ast.literal_eval(cleaned_string)
    list_of_classes = list(list_of_classes)
    return list_of_classes

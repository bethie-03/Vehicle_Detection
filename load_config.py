import yaml

def get_config_yaml(keywords):
    with open('config.yaml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
        requirements_path = config.get(keywords, '')
        return requirements_path
  
        

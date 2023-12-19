import yaml


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def write_yaml(file_path, content):
    with open(file_path, 'w') as file:
        yaml.dump(content, file)
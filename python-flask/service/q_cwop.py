import yaml
from werkzeug.datastructures import FileStorage

def save(file: FileStorage):
    dictionary = yaml.safe_load(file.stream)
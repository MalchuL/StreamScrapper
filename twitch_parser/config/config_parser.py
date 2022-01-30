from omegaconf import OmegaConf

def get_yaml_config(path):
    return OmegaConf.load(path)
import os

def generate_filename(dir: str, name: str, extension: str) -> str:
    return name+"_"+str(len(os.listdir(dir)))+"."+extension
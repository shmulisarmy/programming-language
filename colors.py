def blue(text: str) -> str:
    return f"\033[94m{text}\033[0m"

def green(text: str) -> str:
    return f"\033[92m{text}\033[0m"

def red(text: str) -> str:
    return f"\033[91m{text}\033[0m"

def yellow(text: str) -> str:
    return f"\033[93m{text}\033[0m"

def magenta(text: str) -> str:
    return f"\033[95m{text}\033[0m"

def cyan(text: str) -> str:
    return f"\033[96m{text}\033[0m"

def white(text: str) -> str:
    return f"\033[97m{text}\033[0m"

def reset(text: str) -> str:
    return f"\033[0m{text}\033[0m"
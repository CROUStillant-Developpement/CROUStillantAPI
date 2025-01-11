def getBoolFromString(b: str|bool) -> bool:
    if isinstance(b, bool):
        return b

    if b.lower() == "true":
        return True
    elif b.lower() == "false":
        return False
    else:
        return None

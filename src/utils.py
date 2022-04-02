def class_id(name: str, class_reference) -> str:
    return f"<{name} {hex(id(class_reference))[2:5]}..{hex(id(class_reference))[-3:]}>"

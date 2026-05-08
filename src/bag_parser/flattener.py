def flatten_msg(msg, prefix="", unpack_all_bytes=False):
    result = {}

    slots = msg.__slots__

    for slot_name in slots:
        key = f"{prefix}{slot_name}" if prefix else slot_name
        value = getattr(msg, slot_name)

        if unpack_all_bytes:
            if isinstance(value, bytes):
                for i, b in enumerate(value):
                    result[f"{key}_b{i}"] = b
                continue
            elif isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], int):
                for i, b in enumerate(value):
                    result[f"{key}_b{i}"] = b
                continue

        if hasattr(value, 'secs') and hasattr(value, 'nsecs'):
            result[key] = value.secs + value.nsecs * 1e-9

        elif hasattr(value, '__slots__'):
            nested = flatten_msg(value, prefix=key + ".",
                                 unpack_all_bytes=unpack_all_bytes)
            result.update(nested)

        elif isinstance(value, (list, tuple)):
            if len(value) == 0:
                result[key] = ""
            elif hasattr(value[0], '__slots__'):
                for i, item in enumerate(value):
                    nested = flatten_msg(item, prefix=f"{key}[{i}].",
                                         unpack_all_bytes=unpack_all_bytes)
                    result.update(nested)
            else:
                result[key] = ", ".join(str(v) for v in value)
        else:
            result[key] = value

    return result

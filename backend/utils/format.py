# Helper function to format nested dictionaries/lists for display, flattening keys
def format_nested_dict(d: dict, parent_key_prefix=""):
    items = []
    for k, v in d.items():
        # Construct the new key including the prefix
        key = k.replace("_", " ")
        current_key = f"{parent_key_prefix} {key}" if parent_key_prefix else key

        if isinstance(v, dict):
            # Recursively call with the new key as prefix, extend items
            nested_items = format_nested_dict(v, parent_key_prefix=current_key)
            items.extend(nested_items)
        elif isinstance(v, list):
            # Join list items with commas
            if v: # Only add if the list is not empty
                items.append(f"{current_key}: {', '.join(map(str, v))}")
        elif isinstance(v, int):
            items.append(f"{current_key}: {v if v > 0 else 'not specified'}")
        elif v: # Only add non-empty, non-dict, non-list values
            items.append(f"{current_key}: {v}")
    return items # Return a list of formatted strings

def format_nested_dict_for_prompt(d: dict) -> str:
    return ", ".join(format_nested_dict(d))

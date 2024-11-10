def format_file_size(size_in_bytes: int) -> str:
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_in_bytes)
    for unit in units:
        if size < 1024:
            return f"{size:.2f}".rstrip('0').rstrip('.') + f" {unit}"
        size /= 1024
    return f"{size:.2f} PB"
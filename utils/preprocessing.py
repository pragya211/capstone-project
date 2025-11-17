def fix_line_wrapping(text):
    """
    Fixes broken lines caused by line wrapping in PDFs.
    Joins lines that likely belong together (no punctuation at end).
    """
    lines = text.split('\n')
    merged_lines = []
    buffer = ''
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[-1] not in '.:;?!':
            buffer += ' ' + line
        else:
            full_line = buffer + ' ' + line if buffer else line
            merged_lines.append(full_line.strip())
            buffer = ''
    # In case anything is left in the buffer
    if buffer:
        merged_lines.append(buffer.strip())
    return '\n'.join(merged_lines)

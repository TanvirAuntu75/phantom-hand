import re
with open('backend/app.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '@app.post("/canvas/clear")' in line:
        new_lines.append(line)
        new_lines.append('async def clear_canvas():\n')
        new_lines.append('    if canvas:\n')
        new_lines.append('        if hasattr(canvas, "clear_all"):\n')
        new_lines.append('            canvas.clear_all()\n')
        new_lines.append('        elif hasattr(canvas, "clear"):\n')
        new_lines.append('            canvas.clear()\n')
        new_lines.append('        logger.info("Canvas cleared.")\n')
        new_lines.append('        return {"status": "success", "message": "Canvas cleared"}\n')
        new_lines.append('    raise HTTPException(status_code=500, detail="Canvas not initialized")\n')
        skip = True
    elif skip and '@app.post("/canvas/undo")' in line:
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

with open('backend/app.py', 'w') as f:
    f.write(''.join(new_lines))

with open('backend/app.py', 'r') as f:
    content = f.read()

content = content.replace('''@app.post("/canvas/clear")
async def clear_canvas():
    if canvas:
        # Wrapper method matching requested clear_all()
        if hasattr(canvas, "clear"):

        elif hasattr(canvas, "clear_all"):
            canvas.clear_all()
        logger.info("Canvas cleared.")
        return {"status": "success", "message": "Canvas cleared"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")''', '''@app.post("/canvas/clear")
async def clear_canvas():
    if canvas:
        if hasattr(canvas, "clear_all"):
            canvas.clear_all()
        elif hasattr(canvas, "clear"):
            canvas.clear()
        logger.info("Canvas cleared.")
        return {"status": "success", "message": "Canvas cleared"}
    raise HTTPException(status_code=500, detail="Canvas not initialized")''')

with open('backend/app.py', 'w') as f:
    f.write(content)

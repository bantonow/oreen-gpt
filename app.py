from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cairosvg import svg2png
from fastapi.responses import Response

app = FastAPI()

class SVGInput(BaseModel):
    svg_code: str

@app.post("/convert-svg-to-png", response_class=Response)
async def convert_svg_to_png(svg_input: SVGInput):
    """
    Convert SVG code to PNG format and return the PNG as a response.
    """
    try:
        # Convert SVG to PNG bytes
        png_bytes = svg2png(bytestring=svg_input.svg_code)
        
        # Return the PNG image with the appropriate MIME type
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid SVG input or conversion error.")

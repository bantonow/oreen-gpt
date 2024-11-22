from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from cairosvg import svg2png
import time
import os
import uuid
from starlette.staticfiles import StaticFiles

app = FastAPI()

class SVGInput(BaseModel):
    svg_code: str

# Ensure the 'static/images' directory exists
image_dir = os.path.join("static", "images")
os.makedirs(image_dir, exist_ok=True)

# Custom StaticFiles class to set headers
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        # Set the headers if the file exists
        if response.status_code == 200:
            filename = os.path.basename(path)
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.headers['Content-Type'] = 'image/png'
            response.headers['ngrok-skip-browser-warning'] = "true"
        return response

# Mount the static files directory to serve images with custom headers
app.mount("/images", CustomStaticFiles(directory=image_dir), name="images")

@app.post("/convert-svg-to-png")
async def convert_svg_to_png(svg_input: SVGInput, request: Request):
    try:
        # Log the request details
        print(f"Incoming Request: {request.method} {request.url}")
        print(f"Request Body: {svg_input.svg_code}")

        # Measure processing time
        start_time = time.time()

        # Perform SVG to PNG conversion
        png_bytes = svg2png(bytestring=svg_input.svg_code)

        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"

        # Save the PNG file
        file_path = os.path.join(image_dir, filename)
        with open(file_path, "wb") as f:
            f.write(png_bytes)

        # Construct the URL to the image
        base_url = str(request.base_url).rstrip('/')
        image_url = f"{base_url}/images/{filename}"

        # Log success and processing time
        process_time = time.time() - start_time
        print(f"Conversion successful! Processed in {process_time:.2f} seconds.")
        print(f"Image URL: {image_url}")

        # Return an array of URLs as per the OpenAI documentation
        return [image_url]

    except Exception as e:
        # Log the error details
        print(f"Error during conversion: {e}")
        raise HTTPException(status_code=400, detail="Invalid SVG input or conversion error.")
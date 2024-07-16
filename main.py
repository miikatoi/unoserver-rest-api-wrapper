from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
import requests
import tempfile
import shutil
import base64
import os
import re
import glob

app = FastAPI()

API_URL = "http://127.0.0.1:2004/request"
OUTPUT_FILE = "file.html"


def img_to_base64(img_path):
    """Convert image to base64 string."""
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode("utf-8")
    return b64_string


def find_image_path(image_name):
    """Find the image path in the tmp/unodata-[some string]/ directories."""
    search_pattern = os.path.join("/tmp", "unodata-*", image_name)
    matching_files = glob.glob(search_pattern)
    if matching_files:
        return matching_files[0]
    else:
        return None


def embed_images_in_html(html_path):
    """Embed images in the HTML file as base64."""
    with open(html_path, "r") as html_file:
        html_content = html_file.read()

    # Find all image tags and their src attributes
    img_tags = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', html_content)

    for img_name in img_tags:
        img_path = find_image_path(img_name)
        if img_path:
            img_ext = os.path.splitext(img_path)[1][1:]
            img_base64 = img_to_base64(img_path)
            img_tag = f"data:image/{img_ext};base64,{img_base64}"

            # Replace img src with base64 string in HTML
            html_content = html_content.replace(f'src="{img_name}"', f'src="{img_tag}"')
        else:
            print(f"Warning: {img_name} not found in the expected directories. Skipping.")

    # output_html_path = 'output_' + os.path.basename(html_path)
    output_html_path = html_path
    with open(output_html_path, "w") as output_html_file:
        output_html_file.write(html_content)

    print(f"HTML with embedded images saved as {output_html_path}")


async def convert_libreoffice(
    input_file_path: str,
    output_dir: str,
    input_format: str,
    convert_to: str,
) -> str:
    """
    Use libreoffice to convert various types of files

    This requires that libreoffice-unoserver is running (https://hub.docker.com/r/libreofficedocker/libreoffice-unoserver)
    """
    output_file_name = input_file_path.split("/")[-1].replace(f".{input_format}", f".{convert_to}")
    output_file_path = f"{output_dir}/{output_file_name}"

    files = {
        "file": (input_file_path.split("/")[-1], open(input_file_path, "rb")),
    }
    url = "http://libreoffice-unoserver:2004/request"
    files = {"file": open(input_file_path, "rb")}
    data = {"convert-to": convert_to}

    response = requests.post(url, files=files, data=data)

    with open(output_file_path, "wb") as f:
        f.write(response.content)

    if convert_to == "html":
        embed_images_in_html(html_path=output_file_path)

    return output_file_path


@app.post("/request")
async def convert_file(file: UploadFile = File(...), convert_to: str = Form(alias="convert-to")):
    input_format = file.filename.split(".")[-1]
    input_format = input_format.lower()
    assert len(input_format) > 0

    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, file.filename)
    output_dir = os.path.join(temp_dir, "output")

    with open(input_file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = await convert_libreoffice(
        input_file_path=input_file_path, output_dir=output_dir, input_format=input_format, convert_to=convert_to
    )

    return FileResponse(output_file_path, media_type="text/html")

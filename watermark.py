# watermark.py
from PIL import Image
import ffmpeg
import os

def add_watermark_to_image(input_path, watermark_path, output_path, position=(20, 20)):
    base = Image.open(input_path).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")
    base.paste(watermark, position, mask=watermark)
    base.save(output_path)

def add_watermark_to_video(input_path, watermark_path, output_path, position=(10, 10)):
    input_stream = ffmpeg.input(input_path)
    overlay = ffmpeg.input(watermark_path)
    ffmpeg.output(
        input_stream.video.filter('overlay', x=position[0], y=position[1]),
        input_stream.audio,
        output_path
    ).run(overwrite_output=True)

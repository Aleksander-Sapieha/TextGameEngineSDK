from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

def count_files(directory_path):
    return sum(1 for entry in os.scandir(directory_path) if entry.is_file())

class VideoExporter:
    def __init__(self):
        self.frames_folder = "replay_frames"

        if not os.path.exists(self.frames_folder):
            os.makedirs(self.frames_folder)

        self.frame_number = 0

        try:
            self.font = ImageFont.truetype("consola.ttf", 24)
        except:
            self.font = ImageFont.load_default()

        self.num = count_files("replays")


    def add_frame(self, text):
        img = Image.new(
            "RGB",
            (1000, 700),
            "black"
        )

        draw = ImageDraw.Draw(img)
        text_lines = text.splitlines()
        visible_lines = text_lines[-20:]

        draw.text(
            (30, 30),
            "\n".join(visible_lines),
            font=self.font,
            fill=(255,255,255)
        )

        filename = (
            f"{self.frames_folder}/"
            f"{self.frame_number:05d}.png"
        )

        img.save(filename)

        self.frame_number += 1


    def export(self):

        command = [
            "ffmpeg",
            "-y",
            "-framerate",
            "30",
            "-i",
            f"{self.frames_folder}/%05d.png",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            f"replays/replay{self.num}.mp4"
        ]
        try:
            subprocess.run(command)
        except:
            print("You need to install ffmpeg first!")
            return

        print(
            f"Video exported: replays/replay{self.num}.mp4"
        )
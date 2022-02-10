import os
import jinja2
import tempfile
import subprocess
from pathlib import Path
from typing import Optional
from nonebot.log import logger

dir_path = Path(__file__).parent / "template"


async def tex2pic(equation, fmt="png", border=2, resolution=1000) -> Optional[bytes]:
    try:
        multi_line = True if r"\\" in equation else False

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(dir_path.absolute()))
        )
        template = env.get_template("template.tex")
        tex_file = template.render(
            border=border, multi_line=multi_line, equation=equation
        )

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            tmp_dir = Path(tmp_dir_name)
            tmp_tex = tmp_dir / "tmp.tex"
            tmp_pdf = tmp_dir / "tmp.pdf"
            tmp_out = tmp_dir / ("tmp." + fmt)
            with tmp_tex.open("w") as f:
                f.write(tex_file)

            stdout = open(os.devnull, "w")
            p_open = subprocess.Popen(
                "pdflatex -interaction=nonstopmode -pdf %s" % tmp_tex,
                shell=True,
                cwd=str(tmp_dir),
                stdout=stdout,
                stderr=stdout,
            )
            p_open.wait()
            stdout.close()

            if p_open.returncode != 0:
                return None

            formats = {
                "jpg": "jpg",
                "jpeg": "jpg",
                "png": "png",
                "tiff": "tiff",
                "ppm": "",
            }
            if fmt in formats.keys():
                convert_cmd = f"pdftoppm -r %d -%s %s > %s" % (
                    resolution,
                    formats[fmt],
                    tmp_pdf,
                    tmp_out,
                )
                subprocess.check_call(convert_cmd, shell=True)

            return tmp_out.read_bytes()
    except Exception as e:
        logger.warning(f"Error in tex2pic({equation}): {e}")
        return None

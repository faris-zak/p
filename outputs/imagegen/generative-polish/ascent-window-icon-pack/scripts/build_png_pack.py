from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image


SOURCE = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[1]
PNG_DIR = ROOT / "full" / "png"
FAVICON_DIR = ROOT / "favicon"
SOURCE_DIR = ROOT / "source"
WEB_DIR = ROOT / "web"


def smoothstep(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def remove_navy_background(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    background = np.array([4.0, 10.0, 26.0], dtype=np.float32)

    # Foreground is strongly separated from the selected mark's navy field.
    # A smooth distance matte retains antialiasing while dropping the subtle
    # background texture and avoiding hard threshold edges.
    brightness = np.max(rgb, axis=2)
    alpha = smoothstep((brightness - 34.0) / 46.0)

    # Unblend partially transparent edge pixels from the original navy matte.
    safe_alpha = np.maximum(alpha[..., None], 1e-4)
    foreground = (rgb - (1.0 - safe_alpha) * background) / safe_alpha
    foreground = np.clip(foreground, 0.0, 255.0)

    rgba = np.dstack((foreground, alpha[..., None] * 255.0)).astype(np.uint8)
    rgba[rgba[..., 3] == 0, :3] = 255
    return Image.fromarray(rgba, mode="RGBA")


def export_sizes(image: Image.Image, stem: str) -> None:
    for size in (512, 256, 128, 64, 48, 32, 16):
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(FAVICON_DIR / f"{stem}-{size}.png", optimize=True)


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    FAVICON_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(SOURCE, SOURCE_DIR / "selected-ascent-window-source.png")
    source_image = Image.open(SOURCE).convert("RGB")
    source_image.save(PNG_DIR / "ascent-window-dark.png", optimize=True)

    transparent = remove_navy_background(source_image)
    transparent.save(PNG_DIR / "ascent-window-transparent.png", optimize=True)

    export_sizes(source_image.convert("RGBA"), "ascent-window-dark")
    export_sizes(transparent, "ascent-window-transparent")

    dark_rgba = source_image.convert("RGBA")
    dark_rgba.resize((16, 16), Image.Resampling.LANCZOS).save(WEB_DIR / "favicon-16x16.png", optimize=True)
    dark_rgba.resize((32, 32), Image.Resampling.LANCZOS).save(WEB_DIR / "favicon-32x32.png", optimize=True)
    dark_rgba.resize((180, 180), Image.Resampling.LANCZOS).save(WEB_DIR / "apple-touch-icon.png", optimize=True)
    dark_rgba.resize((192, 192), Image.Resampling.LANCZOS).save(WEB_DIR / "android-chrome-192x192.png", optimize=True)
    dark_rgba.resize((512, 512), Image.Resampling.LANCZOS).save(WEB_DIR / "android-chrome-512x512.png", optimize=True)
    dark_rgba.save(
        WEB_DIR / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


if __name__ == "__main__":
    main()

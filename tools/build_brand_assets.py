"""Package the supplied emblem for web branding and app launchers.

The source artwork is retained intact. SVG framing removes excess outer whitespace
for horizontal wordmarks; launcher exports preserve the square original.
"""
import base64
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / 'static' / 'img'
source = IMAGES / 'app-emblem.png'
encoded = base64.b64encode(source.read_bytes()).decode('ascii')
(IMAGES / 'logo.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
    'viewBox="60 180 1150 810" width="1150" height="810" role="img" aria-label="AutoLedger BD car emblem">'
    '<image width="1254" height="1254" xlink:href="data:image/png;base64,' + encoded + '"/></svg>',
    encoding='utf-8',
)
with Image.open(source) as image:
    image = image.convert('RGB')
    for size in (192, 512):
        image.resize((size, size), Image.Resampling.LANCZOS).save(IMAGES / f'icon-{size}.png')
    maskable = Image.new('RGB', (512, 512), 'white')
    maskable.paste(image.resize((400, 400), Image.Resampling.LANCZOS), (56, 56))
    maskable.save(IMAGES / 'icon-maskable-512.png')
    image.save(IMAGES / 'favicon.ico', format='ICO', sizes=[(32, 32), (48, 48), (64, 64)])

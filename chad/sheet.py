"""Contact sheet of selected seconds: python3 sheet.py out.png 0.5 1.8 ..."""
import sys, subprocess
from PIL import Image
ts = [float(x) for x in sys.argv[2:]]
ids = [int(t * 12) for t in ts]
subprocess.run([sys.executable, "render.py"] + [str(i) for i in ids], check=True, capture_output=True)
cols = 7
sheet = Image.new("RGB", (cols * 216, ((len(ids) + cols - 1) // cols) * 384), "white")
for k, i in enumerate(ids):
    sheet.paste(Image.open(f"build/frames/{i:05d}.png").resize((216, 384)), ((k % cols) * 216, (k // cols) * 384))
sheet.save(sys.argv[1])

"""Open prepared operator in a new Blender 4.5 session"""

import sys
from pathlib import Path

import bpy

def main():
    if bpy.app.version[:2] != (4, 5):
        raise RuntimeError("Blender 4.5 is required")

    from io_scene_r6.blender_preview import import_siege_model

    arguments = sys.argv[sys.argv.index("--") + 1:]
    models = [Path(value) for value in arguments]
    if not models or any(not path.is_file() for path in models):
        raise RuntimeError("One or more exported models are missing")

    # Launcher starts fresh factory scene in separate window
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    for model in models:
        import_siege_model(model)

    print(f"R6 import complete: {len(models)} models.", flush=True)

if __name__ == "__main__":
    main()

# You made it :D
# import in main seems weird but who cares lol
# Aiden seems to like the hex, trust me
# - Shadow

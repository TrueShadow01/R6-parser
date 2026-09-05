# Rainbow Six Siege Forge Extractor

A Windows tool for browsing Rainbow Six Siege operators and exporting them to Blender.

The desktop UI supports operator search, export, live logs, Blender 4.5 add-on installation and opening exported operators in Blender.

## Setup

Requires Windows, 64-bit Python 3.10+, a local Siege installation and a compatible Oodle runtime. Blender 4.5 is the current import validation target.

Run commands from the project directory.

### Install dependencies

```powershell
py -3 -m pip install -r requirements-gui.txt
```

For CLI-only use, install `requirements.txt` instead.

### Configure Oodle

Supply a compatible `oo2core_*_win64.dll` you are authorized to use. Some games that use Oodle include this DLL in their installation folders, you may already have a suitable copy in a game you own. Compatibility is not guaranteed.

Place the DLL beside `main.py`, or point directly to its existing location:

```powershell
$env:R6_OODLE_DLL = "C:\Path\To\oo2core_8_win64.dll"
```

Use your runtime's actual filename. This setting applies to the current PowerShell session, launch the extractor from that session or set the R6_OODLE_DLL path in the Windows Enviroment Variables.

Oodle is not bundled. See [RAD's official Oodle page](https://www.radgametools.com/oodle.htm) for product information and evaluation requests.

### Configure the game folder

Create an ignored `config.py` beside `main.py`:

```python
GAME_DIR = r"D:\Path\To\Tom Clancy's Rainbow Six Siege"
```

Build the asset index:

```powershell
py -3 -B main.py index --all -o output/r6-assets.sqlite
```

Run indexing again after game updates. Registry browsing alone does not require an index.

## Export an operator

```powershell
py -3 -B gui.py
```

Choose the game folder, click **Load operators**, select an operator and click **Export selected operator**.

The UI reads `datapc64.forge`. Export also requires `datapc64_merged_bnk_mesh.forge`, `datapc64_ondemand.depgraphbin` and the project's `output/r6-assets.sqlite` index for that installation.

Files are saved under:

```text
<destination>/<operator-name>/<body-or-head>/<model-UID>/
```

Export attempts every primary group-0 model and excludes alternate groups. It stops on the first failure and keeps completed files. Closing the window waits for the export queue to finish.

## Import into Blender 4.5

1. Close Blender, then click **Install Blender 4.5 add-on** in the UI.
2. Export an operator.
3. Click **Open in Blender** to launch a new Blender window with the exported models and material fixes.

The standard Blender 4.5 installation path is checked first. If it is missing, a file picker lets you select `blender.exe`. Other Blender versions are rejected.

You can also import an existing export through Blender's **File → Import → Rainbow Six Siege Operator** menu. Select the operator folder containing `body` and `head`.

The UI confirms that Blender launched, import errors appear in Blender's system console.

## Known limitations

- Registry discovery was checked against an installation containing 78 operators. Game updates may require parser changes.
- Caveira and Ace received visual checks, other operators may have material or attachment issues.
- Export supports LOD0 glTF. Complete skeleton hierarchy, animations and GLB export are unavailable.
- Shaders approximate the game appearance. Streamed textures and several material effects remain incomplete.
- The UI's 3D preview, material inspector, automatic indexing and batch resume are not implemented yet. Export history and the selected Blender path are remembered only for the current UI session.

## CLI and tests

The CLI also supports archive scanning, resumable raw extraction, asset indexing, catalogs and model discovery:

```powershell
py -3 -B main.py -h
py -3 -B main.py operators --registry
py -3 -B -m unittest discover -s tests -v
```

Use `<command> -h` for command-specific options. Tests use synthetic data and do not require game assets or Oodle.

## Next steps

1. Save the Blender executable path and expose it in the UI.
2. Package the alpha and validate the complete setup/export/import workflow.
3. Add interactive 3D preview and material/texture inspection.

## License and third-party assets

See [LICENSE](LICENSE) for the project license.

Rainbow Six Siege and its assets belong to Ubisoft. Game assets and the proprietary Oodle runtime are not included or covered by this project's license.
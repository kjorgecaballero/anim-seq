# anim-seq

**anim-seq** is a Blender addon for importing sequences of static meshes as shape key animations, and exporting animations as individual frame files.

## Features

- **Import**: Import multiple FBX/OBJ files as shape keys on a single object
- **Export**: Export each frame of an animation as separate files
- **Format Support**: Full FBX and OBJ format compatibility
- **Auto-Updater**: One-click updates with version notifications

## Installation

1. Download the latest `anim-seq.zip` from the releases page
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the downloaded ZIP file
4. Enable the addon by checking the box next to "anim-seq"

## Basic Usage

### Importing Animation Frames

1. Use **File > Import > Mesh Sequence (FBX/OBJ)** or find the import button in the 3D Viewport sidebar
2. Select multiple OBJ/FBX files (e.g., `frame_001.obj`, `frame_002.obj`, etc.)
3. Ensure the correct file extension filter is selected in the file browser
4. Click "Import" to combine all frames into one object with shape keys

### Exporting to Individual Frames

1. In the anim-seq panel, select export format (FBX or OBJ)
2. Set the frame range: **Start**, **End**, and **Step** values
3. Click "Export Frames" - the entire animation will be saved as individual files per frame

## License

This project is licensed under the **GPL-3.0 License** - see the [LICENSE](LICENSE) file for details.

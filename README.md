# anim-seq

**anim-seq** is a Blender addon for importing sequences of static meshes as shape key animations, and exporting animations as individual frame files.

---

## Features

- **Import**: Import multiple OBJ files as shape keys on a single object, or as separate objects with visibility animation.
- **Export**: Export each frame of an animation as individual OBJ files with **vertex colors** support (Blender 3.3+).
- **Frame range control**: Set start, end, and step.
- **Mesh Only filter**: Ignores cameras, lights, armatures, and empties.
- **Auto-Updater**: One‑click updates with version notifications, background checks, and optional automatic installation (based on [CGCookie's blender-addon-updater](https://github.com/CGCookie/blender-addon-updater)).

---

## Installation

1. Download the latest `anim-seq-io_v1.2.0.zip` from the [releases page](https://github.com/kjorgecaballero/anim-seq/releases).
2. In Blender, go to **Edit > Preferences > Add-ons**.
3. Click **Install…** and select the downloaded ZIP file.
4. Enable the addon by checking the box next to **"anim_sequence_io"**.

---

## Basic Usage

### Importing Animation Frames

1. Use **File > Import > OBJ Sequence (.obj)**.
2. Select multiple OBJ files (e.g., `frame_0001.obj`, `frame_0002.obj`, …).
3. Choose the import method:
   - **ShapeKeys**: Combines all frames into a single object with shape keys (recommended for animation).
   - **Separate Objects**: Imports each frame as a separate object with visibility keyframes.
4. Click **"Import"**.

### Exporting to Individual Frames

1. Select the objects you want to export.
2. Use **File > Export > OBJ Sequence (.obj)**.
3. Set the frame range: **Start**, **End**, and **Step**.
4. Enable **Mesh Only** to ignore non‑geometry objects (default: ON).
5. Enable **Vertex Colors** if you want to preserve vertex colours (default: ON).
6. Click **"Export"** – each frame will be saved as a separate OBJ file in the chosen folder.

---

## Auto‑Updater (CGCookie)

This addon includes the **CGCookie Blender Addon Updater** ([GitHub repository](https://github.com/CGCookie/blender-addon-updater)), which provides:

- Automatic background checks for new versions.
- A popup notification when an update is available.
- One‑click installation of the latest release.
- Optional automatic update checks on Blender startup (configurable in preferences).
- The ability to ignore a specific version or defer updates.

The updater is fully integrated into the addon preferences panel, where you can adjust check intervals, manually check for updates, or install a specific version.

---

## License

This project is licensed under the **GPL-3.0 License** – see the [LICENSE](LICENSE) file for details.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## Support

If you encounter any issues, please [open an issue](https://github.com/kjorgecaballero/anim-seq/issues) on GitHub.

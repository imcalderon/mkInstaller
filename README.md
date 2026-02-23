# Installer Building System

A modern Windows installer creation platform that generates both MSI packages and self-extracting executables. Support for both traditional database-driven configurations and modern, project-agnostic JSON manifests.

## ✨ Key Features

- **📂 Manifest-Driven Workflow**: Build installers using project-agnostic JSON manifests (ideal for Bazel/CMake integration).
- **🗄️ Database-Driven Architecture**: Centralized management for complex products and version history.
- **⚙️ State Machine Build Process**: Reliable, repeatable build automation with clear action steps.
- **📦 Dual Output Formats**: Generate both traditional MSI installers and modern self-extracting executables.
- **🚀 Self-Extracting Technology**: Powered by [ModernArchive](https://github.com/imcalderon/ModernArchive) for advanced auto-execution.
- **🎯 Full Bundling**: Automatically packages all dependencies (DLLs, resources) specified in the manifest.

## 🚀 Quick Start (Manifest Mode)

The manifest mode is the recommended way to integrate with modern build systems like Bazel.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a build**:
   ```bash
   python run_installer_build.py --manifest path/to/manifest.json --root path/to/build/artifacts --out ./dist
   ```

### Manifest Format

```json
{
  "product": {
    "name": "MyTool",
    "version": "1.0.0",
    "manufacturer": "MyCompany",
    "description": "A great utility"
  },
  "files": [
    { "path": "app.exe" },
    { "path": "core.dll", "source": "C:/path/to/local/dependency.dll" }
  ]
}
```

## 🏗️ Build Process Architecture

The installer creation follows a state machine pattern:

1. **`load_manifest` / `query_db`**: Ingest project metadata and file lists.
2. **`setenv`**: Initialize environment variables and validate paths.
3. **`create_cabs`**: Create industry-standard cabinet archives.
4. **`buildmsi`**: Generate the Windows Installer MSI package using `msilib`.
5. **`make_pfw`**: Generate a self-extracting executable wrapper using ModernArchive.

## 📋 System Requirements

### Development Environment
- **Python**: 3.10 (Required for `msilib` support)
- **Dependencies**: Flask, SQLAlchemy, Flask-CORS (see requirements.txt)
- **Windows Tools**: MSI building requires Windows with `makecab.exe` available.

## 🏆 Acknowledgments

- **ModernArchive**: For providing the robust self-extracting executable technology.
- **Python MSI Community**: For msilib guidance and best practices.

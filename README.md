# Installer Building System

A modern, database-driven Windows installer creation platform that generates both MSI packages and self-extracting executables. Built with flexibility and automation in mind, this system streamlines the entire installer development workflow from database management to distribution-ready packages.

## ✨ Key Features

- **🗄️ Database-Driven Architecture**: Centralized management of products, features, files, and dependencies
- **🌐 Web-Based Management**: Intuitive browser interface for configuring installer components
- **⚙️ State Machine Build Process**: Reliable, repeatable build automation with clear action steps
- **📦 Dual Output Formats**: Generate both traditional MSI installers and modern self-extracting executables
- **🚀 Self-Extracting Technology**: Powered by ModernArchive for advanced auto-execution capabilities
- **📁 Directory Scanning**: Automatically populate database from existing file structures
- **🔧 Flexible Configuration**: Support for shortcuts, registry entries, custom actions, and properties
- **📊 Build Validation**: Integrated validation and verification of generated installers
- **🎯 Component Management**: Granular control over features, components, and file organization

## 🎯 Use Cases

### Software Distribution
Create professional Windows installers for commercial software, including automatic MSI execution, registry configuration, and shortcut creation.

### Enterprise Deployment
Generate self-extracting packages that combine your application files with configuration scripts, documentation, and automated setup routines.

### Development Workflow
Streamline your build process with database-driven installer generation that integrates seamlessly with CI/CD pipelines.

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize the database
python -m db.init_db
```

### Launch the Management Interface

```bash
# Start the web-based management interface
python start_web_api.py
```

Open your browser to [http://localhost:5000](http://localhost:5000) to access the installer management dashboard.

### Build Your First Installer

```bash
# Configure your project in run_installer_build.py, then run:
python run_installer_build.py
```

Your installer files will be created in the `out` directory.

## 🗄️ Database-Driven Approach

Unlike traditional installer builders that rely on configuration files, our system uses a structured database approach that provides:

### Centralized Management
- **Products**: Define your software products with versions, descriptions, and metadata
- **Features**: Organize functionality into logical feature groups
- **Components**: Group related files and registry entries
- **Files**: Manage source paths, destination locations, and file attributes
- **Directories**: Define installation directory structures
- **Shortcuts**: Configure desktop, start menu, and program shortcuts
- **Properties**: Set MSI properties and installation parameters

### Web Interface Benefits
- **Visual Management**: Point-and-click interface for complex installer configurations
- **Real-time Updates**: Immediate feedback and validation of configuration changes
- **Team Collaboration**: Multiple developers can manage installer components simultaneously
- **Data Integrity**: Database constraints ensure consistent and valid installer definitions

## 📦 Advanced Self-Extracting Technology

Powered by **ModernArchive**, our self-extracting executables offer enterprise-grade distribution capabilities:

### Automatic MSI Execution
```bash
# Create a self-extracting installer that automatically runs your MSI
# The generated .exe will extract files and launch the MSI installer seamlessly
```

### Smart Deployment Options
- **Silent Installation**: Run installers without user intervention
- **Custom Working Directories**: Control where extraction and execution occur  
- **Flexible Execution**: Run batch files, setup executables, or custom commands post-extraction
- **Cross-Platform Compatibility**: Modern C++17 implementation ensures reliable execution

### Distribution Advantages
- **Single File Distribution**: Package everything into one executable
- **No Dependencies**: End users don't need additional extraction tools
- **Professional Appearance**: Custom branded executables with proper metadata
- **Integrity Verification**: Built-in validation ensures files extract correctly

## 🏗️ Build Process Architecture

The installer creation follows a clear state machine pattern with distinct phases:

### 1. Environment Setup (`setenv`)
- Configure build paths and project parameters
- Validate required directories and dependencies
- Set up environment variables for consistent builds

### 2. Database Query (`query_db`)
- Retrieve product, feature, and file information from database
- Validate file paths and component dependencies
- Prepare build manifest with all required components

### 3. MSI Generation (`buildmsi`)
- Create Windows Installer MSI package using msilib
- Generate compressed cabinet (.cab) files for file storage
- Configure MSI tables for features, components, directories, and files
- Set up installation sequences and custom actions

### 4. Cabinet Creation (`create_cabs`)
- Optimize file compression for distribution
- Create industry-standard cabinet archives
- Integrate cabinet files with MSI package structure

### 5. Self-Extracting Package (`make_pfw`)
- Generate self-extracting executable using ModernArchive technology
- Configure auto-execution parameters for MSI installation
- Create professional distribution package ready for deployment

## 📋 Configuration and Management

### Database Schema Overview

```sql
Products          → Features → Components → Files
    ↓                 ↓           ↓
Properties       Shortcuts    Registry
                              CustomActions
```

### Example Project Structure

```
example_project/
├── bin/                    # Application files
│   ├── app.exe
│   ├── config.dll
│   └── resources/
├── docs/                   # Documentation
└── config_template.ini     # Project configuration template
```

### Web Interface Features

- **Product Management**: Create and configure software products
- **Feature Organization**: Define installation features and components  
- **File Management**: Add files, set destinations, configure attributes
- **Shortcut Configuration**: Create desktop and start menu shortcuts
- **Directory Structure**: Define installation directory hierarchy
- **Real-time Validation**: Immediate feedback on configuration issues

## 🛠️ Advanced Usage

### Directory Scanning and Population

Automatically populate your database from existing file structures:

```bash
# Scan a directory and populate the database
python db/scan_directory.py /path/to/your/files \
    --product-name "YourProduct" \
    --version "1.0.0" \
    --manufacturer "Your Company"
```

### Custom Configuration

Modify `run_installer_build.py` to customize build parameters:

```python
class Options:
    root_path = '/path/to/your/project'
    project_name = 'YourProduct'
    output_dir = '/path/to/output'
    # Add custom options as needed
```

### Build Integration

Integrate with CI/CD pipelines:

```bash
# Example Jenkins/GitHub Actions integration
python run_installer_build.py --silent --output-dir ./artifacts
```

## 📊 Database Management

### Initialization and Setup

```bash
# Initialize with example data
python -m db.init_db

# Reset database (destructive)
python -m db.init_db --reset

# Populate with test data
python db/scan_directory.py example_project/
```

### Backup and Migration

```bash
# The SQLite database file (installer.db) can be backed up directly
cp installer.db installer_backup.db

# Or export specific product data through the web interface
```

## 🔧 Extension and Customization

### Adding New Actions

Create custom build steps by inheriting from `InstallerAction`:

```python
from core.action import InstallerAction

class CustomInstallAction(InstallerAction):
    name = 'custom_action'
    
    def do(self, state):
        # Your custom logic here
        logging.info("Running custom installation step")
```

### Database Schema Extensions

Extend the database model in `db/models.py`:

```python
class CustomProperty(Base):
    __tablename__ = 'custom_properties'
    id = Column(Integer, primary_key=True)
    # Add your custom fields
```

## 📋 System Requirements

### Development Environment
- **Python**: 3.7 or higher
- **Dependencies**: Flask, SQLAlchemy, Flask-CORS (see requirements.txt)
- **Windows Tools**: MSI building requires Windows with msilib support
- **Database**: SQLite (included with Python)

### Runtime Requirements
- **Operating System**: Windows 7 or later for MSI generation
- **Disk Space**: Varies based on project size (typically 50MB+ for build artifacts)
- **Memory**: 512MB+ RAM for database operations

## 🧪 Testing and Validation

### Build Verification

The system includes built-in validation:

```bash
# The validate_msi action automatically checks:
# - MSI file integrity
# - Cabinet file structure  
# - File path validation
# - Component dependencies
```

### Example Projects

```bash
# Test with included example
cd example_project
python ../run_installer_build.py

# Verify output in out/ directory
ls out/
# Should contain: ExampleProduct.msi, ExampleProduct_setup.exe
```

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **Database Schema**: Enhanced models for complex installation scenarios
- **Action System**: Additional build actions and validation steps
- **Web Interface**: Improved UI/UX for complex project management
- **Documentation**: Examples, tutorials, and best practices
- **Testing**: Automated testing for various installation scenarios

### Development Setup

```bash
# Clone and set up development environment
git clone [repository]
cd installer-building-system
pip install -r requirements.txt
python -m db.init_db
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **ModernArchive**: For providing the robust self-extracting executable technology
- **Python MSI Community**: For msilib guidance and best practices
- **Open Source Tools**: Flask, SQLAlchemy, and the broader Python ecosystem

---

**Transform your software distribution with professional, database-driven installer creation.** 🚀

*Combine the reliability of MSI packages with the convenience of self-extracting executables, all managed through an intuitive web interface.*

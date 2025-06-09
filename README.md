# Installer Building System

This system provides tools for building Windows installers (MSI and self-extracting EXE) based on a database of products, features, files, and shortcuts.

## Components

- **Core State Machine**: Manages the installer build process through a series of actions
- **Database**: Stores information about products, features, files, shortcuts, and directories
- **Web API**: Provides a user-friendly interface for managing the database
- **Build Scripts**: Scripts for running the installer build process

## Getting Started

### Install Dependencies

```
pip install -r requirements.txt
```

### Initialize the Database

The database is automatically initialized when needed, but you can manually initialize it with:

```
python -m db.init_db
```

### Start the Web API

To start the web-based database management interface:

```
python start_web_api.py
```

Then open your browser to [http://localhost:5000](http://localhost:5000) to manage:
- Products
- Features
- Files
- Shortcuts
- Directories

### Build an Installer

To build an installer:

```
python run_installer_build.py
```

The installer will be created in the `out` directory.

## Configuration

The build process is configured in `run_installer_build.py`. You can modify:

- **Output Directory**: Where the installer files will be created
- **Project Name**: The name of the product to build
- **Root Path**: The root directory containing the files to include

## Build Process

The installer build process consists of the following steps (actions):

1. **setenv**: Set up environment variables and paths
2. **query_db**: Query the database for product information
3. **buildmsi**: Build an MSI installer
4. **create_cabs**: Create cabinet files (handled in buildmsi)
5. **make_pfw**: Create a self-extracting archive

## Database Schema

The database uses SQLAlchemy and includes the following tables:

- **products**: Products with version and description
- **features**: Features that belong to products
- **files**: Files associated with features
- **shortcuts**: Shortcuts associated with features
- **directories**: Installation directories

## Extending the System

### Adding New Actions

1. Create a new action file in the `actions` directory
2. Inherit from `InstallerAction` class
3. Implement the `do` method
4. Add the action to the goal list in `run_installer_build.py`

### Adding Database Fields

1. Update the model in `db/models.py`
2. Update the web API in `web_api/app.py`
3. Update the templates in `web_api/templates/index.html`

## Troubleshooting

- Check logs for errors
- Ensure all paths exist
- Verify that the database contains the expected data
- Check that files specified in the database actually exist on disk

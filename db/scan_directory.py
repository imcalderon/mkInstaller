#!/usr/bin/env python
"""
Directory Scanner for MSI Database Population

This script scans a directory and populates the installer database with:
- Files (with proper attributes)
- Directories
- Components
- Features
- Product information
"""

import os
import sys
import argparse
import configparser
import uuid
import datetime
import logging
import re
import stat
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from db.session import Session, init_db
from db.models import (
    Product, Feature, Component, File, Directory, 
    Property, Registry, CustomAction, Media, Shortcut
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prompt_user(prompt, default=None):
    """Prompt the user for input with an optional default value."""
    if default:
        result = input(f"{prompt} [{default}]: ").strip()
        return result if result else default
    else:
        return input(f"{prompt}: ").strip()

def load_config(config_path):
    """Load configuration from a file."""
    if not os.path.exists(config_path):
        return {}
        
    config = configparser.ConfigParser()
    config.read(config_path)
    
    result = {}
    if 'Product' in config:
        result.update(dict(config['Product']))
    if 'Installation' in config:
        result.update(dict(config['Installation']))
        
    return result

def estimate_directory_size(directory_path):
    """Estimate the total size of files in a directory in KB."""
    total_size = 0
    for dirpath, _, filenames in os.walk(directory_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size // 1024  # Convert to KB

def get_file_version(file_path):
    """Try to extract version information from a file."""
    # Simple version extraction from filename patterns like name-1.2.3.ext
    filename = os.path.basename(file_path)
    match = re.search(r'[-_](\d+\.\d+(\.\d+)?(\.\d+)?)', filename)
    if match:
        return match.group(1)
    return None

def create_directory_structure(session, base_dir, target_base_dir, parent_dir=None):
    """Create directory entries in the database based on the scanned directory structure."""
    base_dir_obj = None
    
    if parent_dir is None:
        # Create the root directory
        base_name = os.path.basename(base_dir)
        base_dir_obj = Directory(
            name=base_name,
            source_path=base_dir,
            target_path=target_base_dir,
            default_dir=base_name
        )
        session.add(base_dir_obj)
        session.flush()  # Ensure ID is generated
        logger.info(f"Created root directory: {base_name}")
    else:
        base_dir_obj = parent_dir
    
    directories = {}
    directories[base_dir] = base_dir_obj
    
    # Walk the directory tree
    for dirpath, dirnames, _ in os.walk(base_dir):
        parent_obj = directories.get(dirpath)
        
        for dirname in dirnames:
            dir_full_path = os.path.join(dirpath, dirname)
            rel_path = os.path.relpath(dir_full_path, base_dir)
            target_path = os.path.join(target_base_dir, rel_path)
            
            dir_obj = Directory(
                name=dirname,
                source_path=dir_full_path,
                target_path=target_path,
                default_dir=dirname,
                parent=parent_obj
            )
            session.add(dir_obj)
            session.flush()
            directories[dir_full_path] = dir_obj
            logger.info(f"Created directory: {rel_path}")
    
    return directories

def process_files(session, base_dir, directories, feature):
    """Process files and create component/file entries."""
    sequence = 1
    file_count = 0
    
    # Walk the directory tree
    for dirpath, _, filenames in os.walk(base_dir):
        if not filenames:
            continue
            
        dir_obj = directories.get(dirpath)
        if not dir_obj:
            logger.warning(f"Directory object not found for {dirpath}")
            continue
        
        # Create a component for this directory
        component_name = f"comp_{os.path.basename(dirpath)}"
        component = Component(
            name=component_name,
            feature=feature,
            directory=dir_obj
        )
        session.add(component)
        session.flush()
        
        # Add files to the component
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, base_dir)
            
            # Get file attributes
            file_size = os.path.getsize(file_path)
            file_version = get_file_version(file_path)
            file_attributes = 0
            
            # Check if file is readonly, hidden, system, etc.
            file_stat = os.stat(file_path)
            if file_stat.st_mode & stat.S_IRUSR and not (file_stat.st_mode & stat.S_IWUSR):
                file_attributes |= 1  # Read-only
                
            # Create file entry
            file_obj = File(
                path=rel_path,
                install_path=filename,  # Default to just the filename in the target directory
                version=file_version,
                size=file_size,
                attributes=file_attributes,
                sequence=sequence,
                component=component,
                feature=feature
            )
            session.add(file_obj)
            
            # Set the first file as the key path for the component
            if component.key_path is None:
                component.key_path = rel_path
                session.flush()
                
            sequence += 1
            file_count += 1
            
            if file_count % 100 == 0:
                logger.info(f"Processed {file_count} files...")
                
    logger.info(f"Total files processed: {file_count}")
    return file_count

def scan_directory_to_db(source_dir, config=None, config_file=None, interactive=True):
    """
    Scan a directory and populate the database with its contents.
    
    Args:
        source_dir: The directory to scan
        config: Dictionary of configuration values
        config_file: Path to a config file
        interactive: Whether to prompt for missing values
    """
    if not os.path.isdir(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")
        return False
        
    # Load config if provided
    config_values = {}
    if config_file and os.path.exists(config_file):
        config_values = load_config(config_file)
        
    # Override with any explicitly provided config
    if config:
        config_values.update(config)
        
    # Ensure we have a database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.info(f"Using existing database: {e}")
        
    # Get product information
    product_name = config_values.get('name')
    product_version = config_values.get('version')
    product_description = config_values.get('description')
    product_manufacturer = config_values.get('manufacturer')
    target_dir = config_values.get('target_dir')
    
    # If interactive, prompt for missing values
    if interactive:
        if not product_name:
            product_name = prompt_user("Product name")
        if not product_version:
            product_version = prompt_user("Product version", "1.0.0")
        if not product_description:
            product_description = prompt_user("Product description", "")
        if not product_manufacturer:
            product_manufacturer = prompt_user("Manufacturer", "")
        if not target_dir:
            target_dir = prompt_user("Target installation directory", 
                                     f"[ProgramFilesFolder]\\{product_manufacturer}\\{product_name}")
    
    # Validate required fields
    if not product_name:
        logger.error("Product name is required")
        return False
        
    # Create a session
    session = Session()
    
    try:
        # Create the product
        product = Product(
            name=product_name,
            version=product_version,
            description=product_description,
            manufacturer=product_manufacturer,
            installation_location=target_dir,
            estimated_size=estimate_directory_size(source_dir)
        )
        session.add(product)
        session.flush()
        logger.info(f"Created product: {product_name} {product_version}")
        
        # Create standard properties
        properties = [
            ("Manufacturer", product_manufacturer),
            ("ProductName", product_name),
            ("ProductVersion", product_version),
            ("ProductLanguage", "1033"),
            ("ARPCONTACT", config_values.get('contact', '')),
            ("ARPURLINFOABOUT", config_values.get('url', '')),
            ("ARPHELPLINK", config_values.get('help_url', '')),
        ]
        
        for name, value in properties:
            if value:
                prop = Property(name=name, value=value, product=product)
                session.add(prop)
        
        # Create a main feature
        main_feature = Feature(
            name="MainFeature",
            title=f"{product_name} Program Files",
            description=f"The main files for {product_name}",
            product=product
        )
        session.add(main_feature)
        session.flush()
        logger.info("Created main feature")
        
        # Create directory structure
        directories = create_directory_structure(session, source_dir, target_dir)
        
        # Process files
        file_count = process_files(session, source_dir, directories, main_feature)
        
        # Create shortcuts if specified
        shortcuts_config = config_values.get('shortcuts', '')
        if shortcuts_config:
            # Parse shortcuts in format: name:target,name2:target2
            shortcuts = [s.strip() for s in shortcuts_config.split(',')]
            for shortcut_def in shortcuts:
                if ':' in shortcut_def:
                    name, target = shortcut_def.split(':', 1)
                    shortcut = Shortcut(
                        name=name.strip(),
                        target=target.strip(),
                        feature=main_feature
                    )
                    session.add(shortcut)
                    logger.info(f"Created shortcut: {name}")
        
        # Create registry entries if specified
        registry_config = config_values.get('registry', '')
        if registry_config:
            # Parse registry in format: root:key:name=value,root:key:name=value
            registry_entries = [r.strip() for r in registry_config.split(',')]
            for reg_def in registry_entries:
                parts = reg_def.split(':', 2)
                if len(parts) >= 3:
                    root, key, name_value = parts
                    if '=' in name_value:
                        name, value = name_value.split('=', 1)
                    else:
                        name, value = name_value, ""
                        
                    # Find a component to associate with
                    component = session.query(Component).first()
                    if component:
                        reg = Registry(
                            root=root.strip(),
                            key=key.strip(),
                            name=name.strip(),
                            value=value.strip(),
                            component=component
                        )
                        session.add(reg)
                        logger.info(f"Created registry entry: {root}\\{key}\\{name}")
        
        # Commit all changes
        session.commit()
        logger.info(f"Successfully populated database with {file_count} files")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error populating database: {e}")
        return False
        
def main():
    parser = argparse.ArgumentParser(description='Scan a directory and populate the installer database')
    parser.add_argument('source_dir', help='Directory to scan')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='Do not prompt for input')
    parser.add_argument('--product-name', help='Product name')
    parser.add_argument('--product-version', help='Product version')
    parser.add_argument('--manufacturer', help='Manufacturer name')
    parser.add_argument('--description', help='Product description')
    parser.add_argument('--target-dir', help='Target installation directory')
    
    args = parser.parse_args()
    
    # Build config from command-line arguments
    config = {}
    if args.product_name:
        config['name'] = args.product_name
    if args.product_version:
        config['version'] = args.product_version
    if args.manufacturer:
        config['manufacturer'] = args.manufacturer
    if args.description:
        config['description'] = args.description
    if args.target_dir:
        config['target_dir'] = args.target_dir
    
    success = scan_directory_to_db(
        args.source_dir,
        config=config,
        config_file=args.config,
        interactive=not args.non_interactive
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

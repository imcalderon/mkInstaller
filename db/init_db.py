# Example script to initialize the new build system database
from db.session import init_db, Session
from db.models import (
    Product, Feature, Component, File, Directory, 
    Property, Registry, CustomAction, Media, Shortcut
)
import os
import sys
import uuid
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_example_project():
    """Populate database with example project data."""
    session = Session()
    # Create product
    product = Product(
        name='ExampleProject',
        version='1.0',
        description='Example project for installer',
        manufacturer='Example Company',
        product_code=str(uuid.uuid4()).upper(),
        upgrade_code=str(uuid.uuid4()).upper()
    )
    session.add(product)
    session.commit()
    
    # Add standard properties
    properties = [
        ("Manufacturer", product.manufacturer),
        ("ProductName", product.name),
        ("ProductVersion", product.version),
        ("ProductLanguage", "1033"),
        ("ARPCONTACT", "support@example.com"),
        ("ARPURLINFOABOUT", "https://www.example.com"),
    ]
    
    for name, value in properties:
        prop = Property(name=name, value=value, product=product)
        session.add(prop)
    
    # Create a main feature
    main_feature = Feature(
        name='MainFeature',
        description='All files in bin',
        title='Main Files',
        product=product
    )
    session.add(main_feature)
    session.commit()
    
    # Create a directory structure
    program_files = Directory(
        name='ProgramFilesFolder',
        default_dir='ProgramFilesFolder'
    )
    session.add(program_files)
    
    manufacturer_dir = Directory(
        name='ManufacturerDir',
        default_dir='Example Company',
        parent=program_files
    )
    session.add(manufacturer_dir)
    
    product_dir = Directory(
        name='INSTALLDIR',
        default_dir='ExampleProject',
        parent=manufacturer_dir
    )
    session.add(product_dir)
    
    bin_dir = Directory(
        name='BinDir',
        default_dir='bin',
        parent=product_dir
    )
    session.add(bin_dir)
    session.commit()
    
    # Create a component
    bin_component = Component(
        name='BinFiles',
        feature=main_feature,
        directory=bin_dir
    )
    session.add(bin_component)
    session.commit()
    
    # Add all files from example_project/bin
    source_bin_dir = os.path.join(os.path.dirname(__file__), '../example_project/bin')
    if os.path.exists(source_bin_dir):
        sequence = 1
        for fname in os.listdir(source_bin_dir):
            fpath = os.path.join('bin', fname)
            source_path = os.path.join(source_bin_dir, fname)
            file_size = os.path.getsize(source_path) if os.path.isfile(source_path) else 0
            
            file_entry = File(
                path=fpath,
                install_path=fname,
                size=file_size,
                sequence=sequence,
                component=bin_component,
                feature=main_feature
            )
            session.add(file_entry)
            sequence += 1
            
            # Set the first file as the key path
            if bin_component.key_path is None and os.path.isfile(source_path):
                bin_component.key_path = fpath
        
        session.commit()
    
    # Create a shortcut
    shortcut = Shortcut(
        name='ExampleProject',
        description='Launch Example Project',
        target='[INSTALLDIR]bin\\archive-2.0.0.exe',
        feature=main_feature,
        directory=product_dir
    )
    session.add(shortcut)
    
    # Create a registry entry
    registry = Registry(
        root='HKLM',
        key='Software\\Example Company\\ExampleProject',
        name='Version',
        value='[ProductVersion]',
        component=bin_component
    )
    session.add(registry)
    
    session.commit()
    logger.info('Populated database for ExampleProject with bin contents.')

def populate_test_data():
    """Populate database with test data from ModernArchive."""
    session = Session()
    # Create product
    product = Product(
        name='ExampleProduct',
        version='1.0',
        description='Example for packaging',
        manufacturer='Example Manufacturer',
        product_code=str(uuid.uuid4()).upper(),
        upgrade_code=str(uuid.uuid4()).upper()
    )
    session.add(product)
    session.commit()
    
    # Create a main feature
    feature = Feature(
        name='TestFeature',
        description='Test feature',
        title='Test Files',
        product=product
    )
    session.add(feature)
    session.commit()
    
    # Create a directory structure
    program_files = Directory(
        name='ProgramFilesFolder',
        default_dir='ProgramFilesFolder'
    )
    session.add(program_files)
    
    product_dir = Directory(
        name='INSTALLDIR',
        default_dir='ExampleProduct',
        parent=program_files
    )
    session.add(product_dir)
    session.commit()
    
    # Add all files from ModernArchive/examples/test_data
    test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ModernArchive/examples/test_data'))
    
    if os.path.exists(test_data_dir):
        # Map to track directories we've created
        dir_map = {None: product_dir}
        
        # Create components and add files
        for root, dirs, files in os.walk(test_data_dir):
            if not files:
                continue
                
            rel_path = os.path.relpath(root, test_data_dir)
            parent_rel_path = os.path.dirname(rel_path) if rel_path != '.' else None
            
            # Create directory if needed
            if rel_path != '.' and rel_path not in dir_map:
                parent_dir = dir_map.get(parent_rel_path, product_dir)
                dir_name = os.path.basename(rel_path)
                
                dir_obj = Directory(
                    name=f"Dir_{dir_name}",
                    default_dir=dir_name,
                    parent=parent_dir
                )
                session.add(dir_obj)
                session.flush()
                dir_map[rel_path] = dir_obj
            
            # Get the directory for this path
            current_dir = dir_map.get(rel_path if rel_path != '.' else None, product_dir)
            
            # Create a component for this directory
            component = Component(
                name=f"Comp_{os.path.basename(root) if rel_path != '.' else 'Root'}",
                feature=feature,
                directory=current_dir
            )
            session.add(component)
            session.flush()
            
            # Add files
            for fname in files:
                file_path = os.path.join(root, fname)
                rel_file_path = os.path.join(rel_path, fname) if rel_path != '.' else fname
                file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                
                file_entry = File(
                    path=rel_file_path,
                    install_path=fname,
                    size=file_size,
                    component=component,
                    feature=feature
                )
                session.add(file_entry)
                
                # Set the first file as the key path
                if component.key_path is None and os.path.isfile(file_path):
                    component.key_path = rel_file_path
        
        session.commit()
        logger.info('Populated database for ExampleProduct with ModernArchive test_data.')
    else:
        logger.warning(f"Test data directory not found: {test_data_dir}")

def reset_database():
    """Reset the database by dropping and recreating all tables."""
    from db.session import engine
    from db.models import Base
    
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    logger.info("Database reset successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        init_db()
        
    populate_example_project()
    populate_test_data()
    logger.info("Database initialized and populated (installer.db)")

import os
import sys
import msilib
from msilib import schema, sequence, text
from msilib import Directory, Feature, CAB, add_data
from db.session import Session
from db.models import Product, Feature as DBFeature, File as DBFile

# --- Config ---
PRODUCT_NAME = 'ExampleProject'
MSI_NAME = 'example_project.msi'
CAB_NAME = 'example_project.cab'
INSTALLDIR = 'INSTALLDIR'

# --- Query DB for files ---
session = Session()
product = session.query(Product).filter_by(name=PRODUCT_NAME).first()
feature = session.query(DBFeature).filter_by(product=product).first()
files = session.query(DBFile).filter_by(feature=feature).all()

# --- Create CAB file ---
import shutil
cab_dir = 'build_cab_temp'
os.makedirs(cab_dir, exist_ok=True)
for f in files:
    src = os.path.join(os.path.dirname(__file__), '..', 'example_project', f.path)
    dst = os.path.join(cab_dir, os.path.basename(f.path))
    shutil.copy2(src, dst)
# Use makecab.exe to create the CAB
cab_path = os.path.abspath(CAB_NAME)
cmd = f'makecab /D CompressionType=LZX /D CompressionMemory=21 /D CabinetName1={CAB_NAME} /D DiskDirectory1=. {cab_dir}\\*.* {CAB_NAME}'
os.system(cmd)
shutil.rmtree(cab_dir)

# --- Create MSI ---
db = msilib.init_database(MSI_NAME, schema, PRODUCT_NAME, msilib.gen_uuid(),
                         PRODUCT_NAME, '1.0.0', 'Example Manufacturer')
msilib.add_tables(db, sequence)

# Directory table
rootdir = Directory(db, 'TARGETDIR', 'SourceDir', None)
installdir = rootdir.add_directory(INSTALLDIR, 'Install Folder')

# Feature table
feature_obj = Feature(db, 'DefaultFeature', 'Default Feature', 'Everything', 1, directory=installdir)

# Add files to the File table and Media table
cab = CAB('example_project', db)
for f in files:
    fname = os.path.basename(f.path)
    cab.add(os.path.join('bin', fname), fname)
    installdir.start_component(fname, msilib.gen_uuid(), 0)
    installdir.add_file(fname, src=fname)
cab.commit(db)
add_data(db, 'Media', [(1, CAB_NAME, None, None, None, None)])

# --- Custom Action DLL (if needed) ---
# To add a custom action DLL, you would use msilib.Binary(db, 'MyAction', 'path_to_dll')
# and add a row to the CustomAction table.

# --- Finalize ---
db.Commit()
print(f"Created {MSI_NAME} and {CAB_NAME}.")

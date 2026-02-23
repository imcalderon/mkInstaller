from core.action import InstallerAction
import logging
import os
import shutil
import tempfile

logger = logging.getLogger("installer.actions.buildmsi")

class InstallerBuildMSIAction(InstallerAction):
    name = 'buildmsi'

    def do(self, state):
        import msilib
        from msilib import schema, sequence
        from msilib import Directory, Feature, CAB, add_data
        
        logging.info("Building installer with msilib...")
        
        # Get output directory from options
        output_dir = getattr(state.library.options, 'output_dir', os.path.abspath('out'))
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if we have files from query_db action
        if not hasattr(state.library, 'files') or not state.library.files:
            logging.warning("No files found to include in MSI. Check query_db action.")
            return
            
        # Prepare a real temp directory for CAB/MSI source
        temp_root = tempfile.mkdtemp(prefix='msi_build_')
        temp_installdir = os.path.join(temp_root, 'INSTALLDIR')
        os.makedirs(temp_installdir, exist_ok=True)
        
        copied_files = []
        for f in state.library.files:
            src = getattr(f, 'abs_source', os.path.join(state.library.root_path, f.path))
            fname = os.path.basename(f.path)
            dst = os.path.join(temp_installdir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                copied_files.append(fname)
                logging.info(f"Copied {src} to {dst}")
        
        if not copied_files:
            logging.error("No files were copied to the temporary directory")
            shutil.rmtree(temp_root)
            return
            
        # Check if CAB was created by create_cabs action
        if not hasattr(state.library, 'cab_name') or not hasattr(state.library, 'cab_path'):
            logging.error("CAB file not found. Make sure create_cabs action ran successfully.")
            shutil.rmtree(temp_root)
            return
            
        cab_name = state.library.cab_name
        
        # Create MSI
        msi_name = f"{state.library.project_name}.msi"
        msi_path = os.path.join(output_dir, msi_name)
        
        # Ensure we have a clean file
        if os.path.exists(msi_path): os.remove(msi_path)

        manufacturer = getattr(state.library.options, 'manufacturer', 'Example Manufacturer')
        version = state.library.product_info.get('version', '1.0.0')
        
        db = msilib.init_database(
            msi_path, 
            schema, 
            state.library.project_name, 
            msilib.gen_uuid(), 
            version, 
            manufacturer
        )
        
        msilib.add_tables(db, sequence)
        
        # Standard Properties
        add_data(db, 'Property', [
            ("SourceDir", os.path.abspath(temp_root)),
            ("DefaultUIFont", "WixUI_Font_Normal"),
        ])
        
        # Use msilib Directory correctly for hierarchy
        cab = CAB(state.library.project_name)
        rootdir = Directory(db, cab, None, 'TARGETDIR', 'SourceDir', 'TARGETDIR')
        rootdir.start_type = 0 # root
        
        # Files go into a subfolder of ProgramFiles
        pfiles = Directory(db, cab, rootdir, 'ProgramFilesFolder', 'PFiles', 'ProgramFilesFolder')
        installdir = Directory(db, cab, pfiles, 'INSTALLDIR', 'MANIFOLD', state.library.project_name)
        
        # Create feature
        feature_obj = Feature(db, 'DefaultFeature', 'Default', 'Main Feature', 1)
        feature_obj.set_current()
        
        for i, f in enumerate(state.library.files, 1):
            fname = os.path.basename(f.path)
            # Use absolute source for the add_file call to ensure it's found in temp_root
            src = os.path.join(temp_installdir, fname)
            
            # Use installdir.add_file to correctly register in File and Component tables
            installdir.add_file(fname, src=src)
        
        # Add Media table entry pointing to our CAB (already created by create_cabs)
        add_data(db, 'Media', [(1, len(state.library.files), None, "#" + cab_name, None, None)])
        
        # Commit the database
        db.Commit()
        
        # Store MSI path in state
        state.library.msi_path = msi_path
        
        # Clean up
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
            
        import stat
        shutil.rmtree(temp_root, onerror=remove_readonly)
        
        logging.info(f"Installer built at: {state.library.msi_path}")

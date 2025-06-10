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
            src = os.path.join(state.library.root_path, f.path)
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
        
        # Create MSI (fix Directory args, ensure _logical is not None)
        msi_name = f"{state.library.project_name}.msi"
        msi_path = os.path.join(output_dir, msi_name)
        
        db = msilib.init_database(
            msi_path, 
            schema, 
            state.library.project_name, 
            msilib.gen_uuid(), 
            state.library.product_info.get('version', '1.0.0'), 
            'Example Manufacturer'
        )
        
        msilib.add_tables(db, sequence)
        
        # Use msilib Directory correctly
        cab = CAB(state.library.project_name)
        
        # Root directory: basedir must be None for TARGETDIR
        rootdir = Directory(db, cab, None, 'TARGETDIR', 'TARGETDIR', 'TARGETDIR')
        installdir = Directory(db, cab, rootdir, 'INSTALLDIR', 'INSTALLDIR', 'Install Folder')
        
        # Create feature
        feature_obj = Feature(db, 'DefaultFeature', 'Default Feature', 'Everything', 1)
        feature_obj.set_current()
        
        # Add files to CAB and MSI
        for fname in copied_files:
            file_path = os.path.join(temp_installdir, fname)
            cabfile = os.path.basename(file_path)
            
            # Add file to CAB
            _, component = cab.append(file_path, cabfile)
            
            # Add file to MSI
            installdir.add_file(
                cabfile,
                src=file_path,
                version=None,
                language=None
            )
            
        # Commit the CAB file
        cab.commit(db)
        
        # Add Media table entry
        add_data(db, 'Media', [(1, cab_name, None, None, None, None)])
        
        # Commit the database
        db.Commit()
        
        # Store MSI path in state
        state.library.msi_path = msi_path
        
        # Clean up
        shutil.rmtree(temp_root)
        
        logging.info(f"Installer built at: {state.library.msi_path}")

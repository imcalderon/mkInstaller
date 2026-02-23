from core.action import InstallerAction
import logging
import os
import json

logger = logging.getLogger("installer.actions.load_manifest")

class ManifestFile:
    """Mock object that behaves like the File database model"""
    def __init__(self, path, size=0, version=None, attributes=0):
        self.path = path
        self.size = size
        self.version = version
        self.attributes = attributes

class LoadManifestAction(InstallerAction):
    name = 'load_manifest'

    def do(self, state):
        manifest_path = getattr(state.library.options, 'manifest', None)
        if not manifest_path or not os.path.exists(manifest_path):
            raise Exception(f"Manifest file not found: {manifest_path}")

        logging.info(f"Loading manifest from {manifest_path}...")
        with open(manifest_path, 'r') as f:
            data = json.load(f)

        # 1. Load Product Info
        product_data = data.get('product', {})
        manifest_project_name = product_data.get('name', getattr(state.library, 'project_name', 'Unknown'))
        
        state.library.product_info = {
            'name': manifest_project_name,
            'version': product_data.get('version', '1.0.0'),
            'description': product_data.get('description', ''),
            'manufacturer': product_data.get('manufacturer', 'Default Manufacturer')
        }
        
        # Ensure project_name is set in library
        state.library.project_name = manifest_project_name

        # 2. Load Feature Info
        feature_data = data.get('feature', {})
        state.library.feature_info = {
            'name': feature_data.get('name', 'MainFeature'),
            'description': feature_data.get('description', 'Main Application Files')
        }

        # 3. Load Files
        manifest_files = data.get('files', [])
        valid_files = []
        
        # Use manifest root_path if provided, otherwise fallback to options
        root_path = product_data.get('root_path', state.library.root_path)
        state.library.root_path = os.path.abspath(root_path)

        for f_data in manifest_files:
            rel_path = f_data.get('path')
            # Use 'source' if provided (absolute path), otherwise use root_path + rel_path
            src_path = f_data.get('source')
            if not src_path:
                src_path = os.path.join(state.library.root_path, rel_path)
            
            src_path = os.path.abspath(src_path)
            
            if os.path.exists(src_path):
                # Auto-calculate size if not provided
                size = f_data.get('size', os.path.getsize(src_path))
                
                f_obj = ManifestFile(
                    path=rel_path,
                    size=size,
                    version=f_data.get('version'),
                    attributes=f_data.get('attributes', 0)
                )
                # Store absolute source path for create_cabs/msi to use
                f_obj.abs_source = src_path
                valid_files.append(f_obj)
            else:
                logging.warning(f"File {src_path} does not exist and will be skipped")

        state.library.files = valid_files
        logging.info(f"Loaded {len(valid_files)} files from manifest")

        # 4. Optional Path Overrides
        paths = data.get('paths', {})
        state.library.project_bin = paths.get('project_bin', state.library.root_path)
        state.library.project_docs = paths.get('project_docs', state.library.root_path)
        state.library.project_shared = paths.get('project_shared', state.library.root_path)

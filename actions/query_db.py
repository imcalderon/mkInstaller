from core.action import InstallerAction
import logging
import os

logger = logging.getLogger("installer.actions.query_db")

class QueryDBAction(InstallerAction):
    name = 'query_db'

    def do(self, state):
        logging.info("Querying database for information...")
        from db.session import Session
        from db.models import Product, Feature, File
        
        session = Session()
        product = session.query(Product).filter_by(name=state.library.project_name).first()
        
        if not product:
            raise Exception(f"Product '{state.library.project_name}' not found in database")
            
        feature = session.query(Feature).filter_by(product=product).first()
        
        if not feature:
            raise Exception(f"No feature found for product '{state.library.project_name}'")
            
        files = session.query(File).filter_by(feature=feature).all()
        
        # Store query results in state
        state.library.product_info = {
            'id': product.id,
            'name': product.name,
            'version': product.version,
            'description': product.description
        }
        
        state.library.feature_info = {
            'id': feature.id,
            'name': feature.name,
            'description': feature.description
        }
        
        # Validate file paths
        valid_files = []
        for file in files:
            src_path = os.path.join(state.library.root_path, file.path)
            if os.path.exists(src_path):
                valid_files.append(file)
            else:
                logging.warning(f"File {src_path} does not exist and will be skipped")
        
        state.library.files = valid_files
        logging.info(f"Found {len(valid_files)} valid files for product '{state.library.project_name}'")

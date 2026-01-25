from db.models import (
    Product, Feature, File, Shortcut, Component, Directory,
    Icon, RegistryEntry, RedistFile, CustomAction, FileAssociation,
    InstallerMeta, Registry, Property, Media
)
from db.session import Session
from sqlalchemy.orm.exc import NoResultFound

def get_component_guid(session, comp_name):
    """Get the component GUID/ID by component name"""
    try:
        comp = session.query(Component).filter_by(name=comp_name).one()
        return comp.component_id
    except NoResultFound:
        return None

def create_component(session, name, component_id=None, directory_id=None, key_path=None, feature_id=None):
    """Create a new component in the database"""
    comp = Component(
        name=name,
        component_id=component_id,
        directory_id=directory_id,
        key_path=key_path,
        feature_id=feature_id
    )
    session.add(comp)
    session.commit()
    return comp

def get_features(session, product_name):
    """Get all features for a product by product name"""
    return session.query(Feature).join(Product).filter(Product.name == product_name).all()

def get_files(session, component):
    """Get all files associated with a component's feature"""
    return session.query(File).filter_by(feature_id=component.feature_id).all()

def get_files_by_feature(session, feature_id):
    """Get all files for a specific feature"""
    return session.query(File).filter_by(feature_id=feature_id).all()

def get_redists(session, product_id, cpu=None):
    """Get redistributable files for a product, optionally filtered by CPU architecture"""
    query = session.query(RedistFile).filter_by(product_id=product_id)
    if cpu:
        query = query.filter_by(cpu=cpu)
    return query.all()

def get_icons(session, product_id):
    """Get all icons for a product"""
    return session.query(Icon).filter_by(product_id=product_id).all()

def get_registry_entries(session, feature_id=None, component_id=None):
    """Get registry entries, optionally filtered by feature or component"""
    query = session.query(RegistryEntry)
    if feature_id:
        query = query.filter_by(feature_id=feature_id)
    if component_id:
        query = query.filter_by(component_id=component_id)
    return query.all()

def get_file_associations(session, feature_id=None):
    """Get file associations, optionally filtered by feature"""
    query = session.query(FileAssociation)
    if feature_id:
        query = query.filter_by(feature_id=feature_id)
    return query.all()

def get_shortcuts(session, feature_id):
    """Get shortcuts for a feature"""
    return session.query(Shortcut).filter_by(feature_id=feature_id).all()

def get_product_by_name(session, product_name):
    """Get a product by name"""
    try:
        return session.query(Product).filter_by(name=product_name).one()
    except NoResultFound:
        return None

def get_directories(session, parent_id=None):
    """Get directories, optionally filtered by parent"""
    query = session.query(Directory)
    if parent_id is not None:
        query = query.filter_by(parent_id=parent_id)
    else:
        query = query.filter(Directory.parent_id.is_(None))
    return query.all()

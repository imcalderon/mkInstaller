from db.models import Product, Feature, File, Shortcut, Component, Directory, Icon, RegistryEntry, RedistFile, CustomAction, FileAssociation, InstallerMeta
from db.session import Session
from sqlalchemy.orm.exc import NoResultFound

def get_component_guid(session, comp_name):
    try:
        comp = session.query(Component).filter_by(name=comp_name).one()
        return comp.guid
    except NoResultFound:
        return None

def create_component(session, name, guid, directory, attributes=0, cpu_type=None, keypath=None, feature=None, shared=False):
    comp = Component(name=name, guid=guid, directory=directory, attributes=attributes, cpu_type=cpu_type, keypath=keypath, feature=feature, shared=shared)
    session.add(comp)
    session.commit()
    return comp

def get_features(session, product_name):
    return session.query(Feature).join(Product).filter(Product.name == product_name).all()

def get_files(session, component):
    return session.query(File).filter_by(feature_id=component.feature_id).all()

def get_redists(session, product_name, cpu):
    return session.query(RedistFile).filter_by(product_name=product_name, cpu=cpu).all()

# Add more helper functions as needed for registry, icons, etc.

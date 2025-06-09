from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    version = Column(String)
    description = Column(Text)
    manufacturer = Column(String)
    product_code = Column(String, default=lambda: str(uuid.uuid4()).upper())  # MSI ProductCode
    upgrade_code = Column(String, default=lambda: str(uuid.uuid4()).upper())  # MSI UpgradeCode
    language = Column(String, default='1033')  # Default to English
    package_code = Column(String, default=lambda: str(uuid.uuid4()).upper())  # MSI PackageCode
    estimated_size = Column(Integer)  # Estimated size in KB
    installation_location = Column(String, default='[ProgramFilesFolder][Manufacturer]\\[ProductName]')
    features = relationship('Feature', back_populates='product', cascade="all, delete-orphan")
    properties = relationship('Property', back_populates='product', cascade="all, delete-orphan")

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    title = Column(String)
    display = Column(Integer, default=1)  # 0=hidden, 1=visible, 2=expanded
    level = Column(Integer, default=1)    # Installation level: 1=required, >1=optional
    parent_id = Column(Integer, ForeignKey('features.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='features')
    files = relationship('File', back_populates='feature', cascade="all, delete-orphan")
    shortcuts = relationship('Shortcut', back_populates='feature', cascade="all, delete-orphan")
    components = relationship('Component', order_by='Component.id', back_populates='feature')
    sub_features = relationship('Feature', backref=relationship.backref('parent', remote_side=[id]))

class Component(Base):
    __tablename__ = 'components'
    id = Column(Integer, primary_key=True)
    component_id = Column(String, default=lambda: str(uuid.uuid4()).upper())  # MSI ComponentId
    name = Column(String, nullable=False)
    key_path = Column(String)  # Key file path for the component
    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship('Feature', back_populates='components')
    directory_id = Column(Integer, ForeignKey('directories.id'))
    directory = relationship('Directory', back_populates='components')
    files = relationship('File', back_populates='component')
    
class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)  # Source path
    install_path = Column(String)          # Destination path (if different)
    version = Column(String)               # File version
    size = Column(Integer)                 # File size in bytes
    attributes = Column(Integer, default=0)  # File attributes
    sequence = Column(Integer)             # Sequence for ordering
    component_id = Column(Integer, ForeignKey('components.id'))
    component = relationship('Component', back_populates='files')
    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship('Feature', back_populates='files')

class Directory(Base):
    __tablename__ = 'directories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    source_path = Column(String)  # Path in source/build location
    target_path = Column(String)  # Path in target installation
    default_dir = Column(String)  # DefaultDir for MSI
    parent_id = Column(Integer, ForeignKey('directories.id'), nullable=True)
    parent = relationship('Directory', remote_side=[id], backref='children')
    components = relationship('Component', back_populates='directory')

class Shortcut(Base):
    __tablename__ = 'shortcuts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    target = Column(String, nullable=False)
    arguments = Column(String)
    working_dir = Column(String)
    icon_path = Column(String)
    icon_index = Column(Integer, default=0)
    directory_id = Column(Integer, ForeignKey('directories.id'))
    directory = relationship('Directory')
    feature_id = Column(Integer, ForeignKey('features.id'))
    feature = relationship('Feature', back_populates='shortcuts')

class Property(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='properties')

class Registry(Base):
    __tablename__ = 'registry'
    id = Column(Integer, primary_key=True)
    root = Column(String, nullable=False)  # HKLM, HKCU, etc.
    key = Column(String, nullable=False)   # Registry key
    name = Column(String)                 # Value name (NULL for default)
    value = Column(String)                # Registry value
    component_id = Column(Integer, ForeignKey('components.id'))
    component = relationship('Component')

class CustomAction(Base):
    __tablename__ = 'custom_actions'
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)  # Action name
    type = Column(Integer, nullable=False)   # Action type code
    source = Column(String)                 # Source of custom action
    target = Column(String)                 # Target/command
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product')

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    disk_id = Column(Integer, nullable=False)
    cabinet = Column(String)
    volume_label = Column(String)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product')

class InstallerMeta(Base):
    __tablename__ = 'installer_meta'
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# --- Usage Example ---
# engine = create_engine('sqlite:///installer.db')
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()
# # Add/query objects using session

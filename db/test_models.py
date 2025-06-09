import unittest
import os
from db.session import init_db, Session
from db.models import Product, Feature, File, Shortcut, Component, Directory, Icon, RegistryEntry, RedistFile, CustomAction, FileAssociation

class TestDBModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a test database
        cls.db_path = 'test_installer.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from db.models import Base
        cls.engine = create_engine(f'sqlite:///{cls.db_path}')
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_create_product_and_feature(self):
        product = Product(name='TestProduct', version='1.0', description='A test product')
        self.session.add(product)
        self.session.commit()
        feature = Feature(name='TestFeature', description='A test feature', product=product)
        self.session.add(feature)
        self.session.commit()
        self.assertEqual(self.session.query(Product).count(), 1)
        self.assertEqual(self.session.query(Feature).count(), 1)

    def test_create_component(self):
        directory = Directory(name='APPDIR')
        self.session.add(directory)
        self.session.commit()
        feature = Feature(name='Feature2', description='desc', product=Product(name='P2'))
        self.session.add(feature)
        self.session.commit()
        comp = Component(name='Comp1', guid='GUID1', directory=directory, feature=feature)
        self.session.add(comp)
        self.session.commit()
        self.assertEqual(self.session.query(Component).count(), 1)

    def test_create_file(self):
        feature = Feature(name='Feature3', description='desc', product=Product(name='P3'))
        self.session.add(feature)
        self.session.commit()
        file = File(path='file.txt', feature=feature)
        self.session.add(file)
        self.session.commit()
        self.assertEqual(self.session.query(File).count(), 1)

if __name__ == '__main__':
    unittest.main()

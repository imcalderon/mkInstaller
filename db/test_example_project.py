import unittest
import os
import shutil
from ModernArchive.examples import test_data
from db.session import init_db, Session
from db.models import Product, Feature, File, Shortcut

class TestExampleProjectPackaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup a clean test db
        cls.db_path = 'test_installer.db'
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        init_db()
        cls.session = Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_package_test_data(self):
        # Simulate adding a product and packaging test_data
        product = Product(name='ExampleProduct', version='1.0', description='Example for packaging')
        self.session.add(product)
        self.session.commit()
        feature = Feature(name='TestFeature', description='Test feature', product=product)
        self.session.add(feature)
        self.session.commit()
        # Add all files from ModernArchive/examples/test_data
        test_data_dir = os.path.join(os.path.dirname(__file__), '../../ModernArchive/examples/test_data')
        for root, dirs, files in os.walk(test_data_dir):
            for fname in files:
                rel_path = os.path.relpath(os.path.join(root, fname), test_data_dir)
                file_entry = File(path=rel_path, feature=feature)
                self.session.add(file_entry)
        self.session.commit()
        self.assertGreater(self.session.query(File).count(), 0)

if __name__ == '__main__':
    unittest.main()

# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_find(self):
        """It should Reade a product by id"""
        product = ProductFactory()
        logger.debug("Creating %s", product.name)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update(self):
        """It should Update a Product"""
        product = ProductFactory()
        logger.debug("Creating %s", product.name)
        product.id = None
        product.create()
        original_id = product.id
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product.description = "test_description"
        product.update()
        products = Product.all()
        self.assertEqual(len(products), 1)
        updated_product = Product.find(product.id)
        self.assertEqual(updated_product.id, original_id)
        self.assertEqual(updated_product.description, "test_description")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "test_description")

    def test_delete(self):
        """It should Delete a Product"""
        product = ProductFactory()
        logger.debug("Creating %s", product.name)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_all(self) -> list:
        """It should return all of the Products in the database"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            logger.debug("Creating %s", product.name)
            product.id = None
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self) -> list:
        """It should return all Products with the given name"""
        for _ in range(10):
            product = ProductFactory()
            logger.debug("Creating %s", product.name)
            product.id = None
            product.create()
        products = Product.all()
        name = products[0].name
        count = 0
        for product in products:
            if product.name == name:
                count += 1
        self.assertEqual(Product.find_by_name(name).count(), count)
        for product in Product.find_by_name(name):
            self.assertEqual(product.name, name)

    def test_find_by_availability(self) -> list:
        """It shoud return all Products by their availability"""
        for _ in range(10):
            product = ProductFactory()
            logger.debug("Creating %s", product.name)
            product.id = None
            product.create()
        products = Product.all()
        availability = products[0].available
        count = 0
        for product in products:
            if product.available == availability:
                count += 1
        self.assertEqual(Product.find_by_availability(availability).count(), count)
        for product in Product.find_by_availability(availability):
            self.assertEqual(product.available, availability)

    def test_find_by_category(self) -> list:
        """It should return all Products by their Category"""
        for _ in range(10):
            product = ProductFactory()
            logger.debug("Creating %s", product.name)
            product.id = None
            product.create()
        products = Product.all()
        category = products[0].category
        count = 0
        for product in products:
            if product.category == category:
                count += 1
        self.assertEqual(Product.find_by_category(category).count(), count)
        for product in Product.find_by_category(category):
            self.assertEqual(product.category, category)

    def test_find_by_price(self) -> list:
        """It should return all Products by their Price"""
        for _ in range(10):
            product = ProductFactory()
            logger.debug("Creating %s", product.name)
            product.id = None
            product.create()
        products = Product.all()
        price = products[0].price
        count = 0
        for product in products:
            if product.price == price:
                count += 1
        self.assertEqual(Product.find_by_price(price).count(), count)
        self.assertEqual(Product.find_by_price(str(price)).count(), count)
        for product in Product.find_by_price(price):
            self.assertEqual(product.price, price)

    def test_update_vealidatiion_error(self):
        """It should raise validation error if id is empty"""
        product = ProductFactory()
        logger.debug("Creating %s", product.name)
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        product.description = "test_description"
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_no_valid_availability_vealidatiion_error(self):
        """It should raise Validation error if availability is not bool"""
        product = ProductFactory()
        data = {"name": "Fedora",
                "description": "A red hat",
                "price": 12.50,
                "available": "Test",
                "category": Category.CLOTHS}
        with self.assertRaises(DataValidationError):
            product.deserialize(data=data)

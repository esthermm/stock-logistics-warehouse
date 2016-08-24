# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# (c) 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class TestStockInventoryPreparationFilterCategories(common.TransactionCase):

    def setUp(self):
        super(TestStockInventoryPreparationFilterCategories, self).setUp()
        self.inventory_model = self.env['stock.inventory']
        # Create a category
        self.category = self.env['product.category'].create(
            {
                'name': 'Category for inventory',
                'type': 'normal',
            })
        # Create some products in the category
        self.product1 = self.env['product.product'].create(
            {
                'name': 'Product for inventory 1',
                'type': 'product',
                'categ_id': self.category.id,
                'default_code': 'PROD1',
            }
        )
        self.product2 = self.env['product.product'].create(
            {
                'name': 'Product for inventory 2',
                'type': 'product',
                'categ_id': self.category.id,
                'default_code': 'PROD2',
            }
        )
        # Product without stock
        self.product3 = self.env['product.product'].create(
            {
                'name': 'Product for inventory 3',
                'type': 'product',
                'categ_id': self.category.id,
                'default_code': 'PROD3',
            }
        )
        # And have some stock in a location
        self.location = self.env['stock.location'].create(
            {
                'name': 'Inventory tests',
                'usage': 'internal',
            }
        )
        inventory = self.inventory_model.create(
            {
                'name': 'Product1 inventory',
                'filter': 'product',
                'line_ids': [
                    (0, 0, {
                        'product_id': self.product1.id,
                        'product_uom_id': self.env.ref(
                            "product.product_uom_unit").id,
                        'product_qty': 2.0,
                        'location_id': self.location.id,
                    }),
                    (0, 0, {
                        'product_id': self.product2.id,
                        'product_uom_id': self.env.ref(
                            "product.product_uom_unit").id,
                        'product_qty': 4.0,
                        'location_id': self.location.id,
                    }),
                ],
            })
        inventory.action_done()

    def test_inventory_category_filter(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Category inventory',
                'filter': 'categories',
                'location_id': self.location.id,
                'categ_ids': [(6, 0, [self.category.id])],
            }
        )
        all_inventory = inventory.copy()
        # Base inventory
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)
        inventory.action_done()
        # All inventory
        all_inventory.all_products = True
        all_inventory = self.inventory_model.create(
            {
                'name': 'Category inventory with all products',
                'filter': 'categories',
                'location_id': self.location.id,
                'categ_ids': [(6, 0, [self.category.id])],
                'all_products': True,
            }
        )
        all_inventory.prepare_inventory()
        self.assertEqual(len(all_inventory.line_ids), 3)
        line3 = all_inventory.line_ids[2]
        self.assertEqual(line3.product_id, self.product3)
        self.assertEqual(line3.theoretical_qty, 0.0)
        self.assertEqual(line3.location_id, self.location)

    def test_inventory_products_filter(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'products',
                'location_id': self.location.id,
                'product_ids': [(6, 0, [self.product1.id, self.product2.id,
                                        self.product3.id])],
            }
        )
        all_inventory = inventory.copy()
        # Base inventory
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.location_id, self.location)
        inventory.action_done()
        # All inventory
        all_inventory.all_products = True
        all_inventory.prepare_inventory()
        self.assertEqual(len(all_inventory.line_ids), 3)
        line3 = all_inventory.line_ids[2]
        self.assertEqual(line3.product_id, self.product3)
        self.assertEqual(line3.theoretical_qty, 0.0)
        self.assertEqual(line3.location_id, self.location)

    def test_inventory_empty_filter(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'empty',
                'location_id': self.location.id,
                'empty_line_ids': [
                    (0, 0, {
                        'product_code': 'PROD1',
                        'product_qty': 3.0,
                    }),
                    (0, 0, {
                        'product_code': 'PROD2',
                        'product_qty': 7.0,
                    }),
                    (0, 0, {
                        'product_code': 'PROD3',
                        'product_qty': 5.0,
                    }),
                ],
            }
        )
        all_inventory = inventory.copy()
        # Base inventory
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        line1 = inventory.line_ids[0]
        self.assertEqual(line1.product_id, self.product1)
        self.assertEqual(line1.theoretical_qty, 2.0)
        self.assertEqual(line1.product_qty, 3.0)
        self.assertEqual(line1.location_id, self.location)
        line2 = inventory.line_ids[1]
        self.assertEqual(line2.product_id, self.product2)
        self.assertEqual(line2.theoretical_qty, 4.0)
        self.assertEqual(line2.product_qty, 7.0)
        self.assertEqual(line2.location_id, self.location)
        inventory.action_done()
        # All inventory
        all_inventory.all_products = True
        all_inventory.empty_line_ids = [
            (0, 0, {
                'product_code': 'PROD1',
                'product_qty': 3.0,
            }),
            (0, 0, {
                'product_code': 'PROD2',
                'product_qty': 7.0,
            }),
            (0, 0, {
                'product_code': 'PROD3',
                'product_qty': 5.0,
            }),
        ]
        all_inventory.prepare_inventory()
        self.assertEqual(len(all_inventory.line_ids), 3)
        line3 = all_inventory.line_ids[2]
        self.assertEqual(line3.product_id, self.product3)
        self.assertEqual(line3.theoretical_qty, 0.0)
        self.assertEqual(line3.product_qty, 5.0)
        self.assertEqual(line3.location_id, self.location)

    def test_inventory_none_filter_all_products(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'none',
                'location_id': self.location.id,
            }
        )
        all_inventory = inventory.copy()
        # Base inventory
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 2)
        inventory.action_done()
        # All inventory
        all_inventory.all_products = True
        all_inventory.prepare_inventory()
        self.assertEqual(len(all_inventory.line_ids), 49)

    def test_inventory_product_filter_all_products(self):
        inventory = self.inventory_model.create(
            {
                'name': 'Products inventory',
                'filter': 'product',
                'location_id': self.location.id,
                'product_id': self.product3.id,
            }
        )
        all_inventory = inventory.copy()
        # Base inventory
        inventory.prepare_inventory()
        self.assertEqual(len(inventory.line_ids), 0)
        inventory.action_done()
        # All inventory
        all_inventory.all_products = True
        all_inventory.prepare_inventory()
        self.assertEqual(len(all_inventory.line_ids), 1)

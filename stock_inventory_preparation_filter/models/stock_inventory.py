# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# (c) 2015 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, models


class StockInventoryEmptyLines(models.Model):
    _name = 'stock.inventory.line.empty'

    product_code = fields.Char(
        string='Product Code', size=64, required=True)
    product_qty = fields.Float(
        string='Quantity', required=True, default=1.0)
    inventory_id = fields.Many2one(
        comodel_name='stock.inventory', string='Inventory',
        required=True, ondelete="cascade")


class StockInventoryFake(object):
    def __init__(self, inventory, product=None, lot=None):
        self.id = inventory.id
        self.location_id = inventory.location_id
        self.product_id = product
        self.lot_id = lot
        self.partner_id = inventory.partner_id
        self.package_id = inventory.package_id


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def _get_inventory_line_value(self, inventory, product):
        vals = []
        product_line = {}
        product_line['inventory_id'] = inventory.id
        product_line['theoretical_qty'] = 0
        product_line['product_id'] = product.id
        product_line['product_uom_id'] = product.uom_id.id
        product_line['location_id'] = inventory.location_id.id
        product_line['package_id'] = inventory.package_id.id
        product_line['partner_id'] = inventory.partner_id.id
        vals.append(product_line)
        return vals

    @api.model
    def _get_available_filters(self):
        """This function will return the list of filters allowed according to
        the options checked in 'Settings/Warehouse'.

        :return: list of tuple
        """
        res_filters = super(StockInventory, self)._get_available_filters()
        res_filters.append(('categories', _('Selected Categories')))
        res_filters.append(('products', _('Selected Products')))
        for res_filter in res_filters:
            if res_filter[0] == 'lot':
                res_filters.append(('lots', _('Selected Lots')))
        res_filters.append(('empty', _('Empty list')))
        return res_filters

    filter = fields.Selection(
        selection=_get_available_filters, string='Selection Filter',
        required=True)
    categ_ids = fields.Many2many(
        comodel_name='product.category', relation='rel_inventories_categories',
        column1='inventory_id', column2='category_id', string='Categories')
    product_ids = fields.Many2many(
        comodel_name='product.product', relation='rel_inventories_products',
        column1='inventory_id', column2='product_id', string='Products')
    lot_ids = fields.Many2many(
        comodel_name='stock.production.lot', relation='rel_inventories_lots',
        column1='inventory_id', column2='lot_id', string='Lots')
    empty_line_ids = fields.One2many(
        comodel_name='stock.inventory.line.empty', inverse_name='inventory_id',
        string='Capture Lines')
    all_products = fields.Boolean(
        default=False, help='If this field is active, the inventory will show '
        'ALL products that comply with the selected filter.',
        string='Show all products')

    @api.multi
    def _check_all_products(self, inventory, product):
        if inventory.all_products:
            return self._get_inventory_line_value(inventory, product)

    @api.model
    def _get_inventory_lines(self, inventory):
        vals = []
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        if inventory.all_products and inventory.filter == 'product' and \
                not len(vals):
            vals += self._get_inventory_line_value(
                inventory, inventory.product_id)
        elif inventory.filter == 'none' and inventory.all_products:
            vals = super(StockInventory, self)._get_inventory_lines(inventory)
            product_quant = []
            for prod in vals:
                product_quant.append(prod['product_id'])
            products = self.env['product.product'].search([
                ('id', 'not in', product_quant),
                ('type', '=', 'product')])
            for line in products:
                vals += self._get_inventory_line_value(inventory, line)
        elif inventory.filter in ('categories', 'products'):
            products = product_obj
            if inventory.filter == 'categories':
                product_tmpls = product_tmpl_obj.search(
                    [('categ_id', 'in', inventory.categ_ids.ids)])
                products = product_obj.search(
                    [('product_tmpl_id', 'in', product_tmpls.ids)])
            elif inventory.filter == 'products':
                products = inventory.product_ids
            for product in products:
                fake_inventory = StockInventoryFake(inventory, product=product)
                res = super(StockInventory, self)._get_inventory_lines(
                    fake_inventory) or self._check_all_products(
                    inventory, product) or []
                vals += res
        elif inventory.filter == 'lots':
            for lot in inventory.lot_ids:
                fake_inventory = StockInventoryFake(inventory, lot=lot)
                res = super(StockInventory, self)._get_inventory_lines(
                    fake_inventory) or self._check_all_products(
                    inventory, product) or []
                vals += res
        elif inventory.filter == 'empty':
            tmp_lines = {}
            empty_line_obj = self.env['stock.inventory.line.empty']
            for line in inventory.empty_line_ids:
                if line.product_code in tmp_lines:
                    tmp_lines[line.product_code] += line.product_qty
                else:
                    tmp_lines[line.product_code] = line.product_qty
            inventory.empty_line_ids.unlink()
            for product_code in tmp_lines.keys():
                products = product_obj.search([
                    '|', ('default_code', '=', product_code),
                    ('ean13', '=', product_code),
                ])
                if products:
                    product = products[0]
                    fake_inventory = StockInventoryFake(
                        inventory, product=product)
                    values = super(StockInventory, self)._get_inventory_lines(
                        fake_inventory)
                    if values:
                        values[0]['product_qty'] = tmp_lines[product_code]
                    elif not values and inventory.all_products:
                        values = self._get_inventory_line_value(
                            inventory, product)
                        values[0]['product_qty'] = tmp_lines[product_code]
                    else:
                        empty_line_obj.create(
                            {
                                'product_code': product_code,
                                'product_qty': tmp_lines[product_code],
                                'inventory_id': inventory.id,
                            })
                    vals += values
        else:
            vals = super(StockInventory, self)._get_inventory_lines(
                inventory)
        return vals

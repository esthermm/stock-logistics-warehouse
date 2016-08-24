# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Extended Inventory Preparation Filters",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Esther Martín <esthermartin@avanzosc.es>",
    ],
    "category": "Inventory, Logistic, Storage",
    "website": "http://www.odoomrp.com",
    "summary": "More filters for inventory adjustments",
    "data": [
        "views/stock_inventory_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}

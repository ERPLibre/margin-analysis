# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Margins percent in Sales Orders Line',
    'version': '1.0',
    'category': 'Sales',
    'description': """
This module adds the 'Margin Percent' on sales order.
=====================================================

This gives the profitability by calculating the difference between the Unit
Price and Cost Price.
    """,
    'depends': ['sale', 'sale_management', 'sale_margin'],
    'data': ['views/sale_margin_view.xml'],
}

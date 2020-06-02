# Copyright 2020 TechnoLibre (http://technolibre.ca)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Margin Editor",
    "summary": "Edit margin in sale order",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "author": "TechnoLibre",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        'sale_margin',
        'sale_margin_security',
    ],
    "data": [
        'views/sale_order_margin_view.xml',
    ]
}

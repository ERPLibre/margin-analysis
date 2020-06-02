from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_percent = fields.Float(string="Margin Percent", compute='_product_margin_percent',
                                  digits=dp.get_precision('Product Price'), store=False)

    @api.depends('margin')
    def _product_margin_percent(self):
        for line in self:
            if line.price_subtotal:
                line.margin_percent = (line.margin / line.price_subtotal) * 100.
            else:
                line.margin_percent = 0.

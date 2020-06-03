# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api, fields
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    margin_global_edit = fields.Float(
        string="Margin (%)",
        digits=dp.get_precision('Product Price'),
        help="Update all margin.")
    margin_global_product = fields.Float(
        string="Product Margin (%)",
        digits=dp.get_precision('Product Price'),
        help="Update product margin only. Set to 0 to resume global updating effect.")
    margin_global_service = fields.Float(
        string="Service Margin (%)",
        digits=dp.get_precision('Product Price'),
        help="Update service margin only. Set to 0 to resume global updating effect.")

    @api.onchange('margin_global_edit')
    def margin_edit_change(self):
        if not self.margin_global_product:
            self.margin_global_product = self.margin_global_edit
            self.margin_product_edit_change(ignore_update_sale_margin=True)
        if not self.margin_global_service:
            self.margin_global_service = self.margin_global_edit
            self.margin_service_edit_change(ignore_update_sale_margin=True)
        self._product_margin()

    @api.onchange('margin_global_product')
    def margin_product_edit_change(self, ignore_update_sale_margin=False):
        has_change = False
        for line in self.order_line:
            if line.product_id.type != "service" and not line.margin_lock:
                self._update_line_margin_edit(line, self.margin_global_product)
                has_change = True
        if not ignore_update_sale_margin and has_change:
            self._product_margin()

    @api.onchange('margin_global_service')
    def margin_service_edit_change(self, ignore_update_sale_margin=False):
        has_change = False
        for line in self.order_line:
            if line.product_id.type == "service" and not line.margin_lock:
                self._update_line_margin_edit(line, self.margin_global_service)
                has_change = True
            if not ignore_update_sale_margin and has_change:
                self._product_margin()

    def _update_line_margin_edit(self, line, marge):
        marge_percent = marge / 100
        if line.purchase_price:
            line.margin_edit = marge_percent * line.purchase_price
        else:
            line.margin_edit = marge_percent
        line.price_unit = line.purchase_price + line.margin_edit


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_edit = fields.Float(string="Margin ($)",
                               digits=dp.get_precision('Product Price'))

    margin_lock = fields.Boolean(string="Lock margin", default=False,
                                 help="Don't be affect by global marge.")

    @api.onchange('margin_edit', 'purchase_price')
    def margin_edit_change(self):
        self.price_unit = self.purchase_price + self.margin_edit
        self._product_margin()

    # @api.onchange('product_uom_qty')
    # def margin_total_change(self):
    #     self._product_margin()
    #     self.order_id._product_margin()
    #     print(self.order_id.margin)

    @api.onchange('price_unit')
    def price_unit_margin_change(self):
        self.margin_edit = self.price_unit - self.purchase_price

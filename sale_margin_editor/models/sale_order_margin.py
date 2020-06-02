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
            self.margin_product_edit_change()
        if not self.margin_global_service:
            self.margin_global_service = self.margin_global_edit
            self.margin_service_edit_change()

    @api.onchange('margin_global_product')
    def margin_product_edit_change(self):
        has_change = False
        for line in self.order_line:
            if line.product_id.type != "service" and not line.margin_lock:
                marge_percent = self.margin_global_product / 100
                if line.purchase_price:
                    line.margin_edit = marge_percent * line.purchase_price
                else:
                    line.margin_edit = marge_percent
                line.price_unit = line.purchase_price + line.margin_edit
                has_change = True
        if has_change:
            self._product_margin()

    @api.onchange('margin_global_service')
    def margin_service_edit_change(self):
        has_change = False
        for line in self.order_line:
            if line.product_id.type == "service" and not line.margin_lock:
                marge_percent = self.margin_global_service / 100
                if line.purchase_price:
                    line.margin_edit = marge_percent * line.purchase_price
                else:
                    line.margin_edit = marge_percent
                line.price_unit = line.purchase_price + line.margin_edit
                has_change = True
        if has_change:
            self._product_margin()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_edit = fields.Float(string="Margin ($)",
                               digits=dp.get_precision('Product Price'))

    margin_percent_edit = fields.Float(string="Margin (%)",
                                       digits=dp.get_precision('Product Price'))

    margin_lock = fields.Boolean(string="Lock margin", default=False,
                                 help="When update manually, lock the margin to block "
                                      "update by global margin.")

    # margin_focus_percent_lock = fields.Boolean(
    #     string="Lock margin on percent", default=True,
    #     help="Base on percent margin when update other fields. "
    #          "Set it true when last change value is margin_percent.")

    @api.onchange('margin_edit')
    def margin_edit_change(self):
        # self.margin_focus_percent_lock = False
        self.margin_lock = bool(self.product_id)
        self.price_unit = self.purchase_price + self.margin_edit
        if self.purchase_price:
            self.margin_percent_edit = ((self.purchase_price + self.margin_edit) / \
                                        self.purchase_price - 1) * 100
        else:
            self.margin_percent_edit = 999999
        # self._product_margin()

    @api.onchange('margin_percent_edit')
    def margin_percent_change(self):
        # self.margin_focus_percent_lock = True
        self.margin_lock = bool(self.product_id)
        self.margin_edit = self.margin_percent_edit / 100. * self.purchase_price
        self.price_unit = self.purchase_price + self.margin_edit
        # self._product_margin()

    @api.onchange('purchase_price')
    def purchase_price_margin_change(self):
        # if self.purchase_price:
        #     self.margin_percent_edit = ((self.purchase_price + self.margin_edit) / \
        #                                 self.purchase_price - 1) * 100
        # else:
        #     self.margin_percent_edit = 999999
        self.margin_edit = self.margin_percent_edit / 100. * self.purchase_price
        # if self.margin_focus_percent_lock:
        #     self.margin_edit = self.margin_percent_edit / 100. * self.purchase_price
        # elif self.purchase_price:
        #     self.margin_percent_edit = ((self.purchase_price + self.margin_edit) / \
        #                                 self.purchase_price - 1) * 100
        # else:
        #     self.margin_percent_edit = 999999

        self.price_unit = self.purchase_price + self.margin_edit

        self._product_margin()

    @api.onchange('price_unit')
    def price_unit_margin_change(self):
        # if self.margin_focus_percent_lock:
        #     self.margin_edit = self.price_unit / self.purchase_price - 1
        # else:
        #     self.margin_edit = self.price_unit - self.purchase_price
        self.margin_edit = self.price_unit - self.purchase_price
        if self.purchase_price:
            self.margin_percent_edit = (self.price_unit / self.purchase_price - 1) * 100
        else:
            self.margin_percent_edit = 999999
        self._product_margin()

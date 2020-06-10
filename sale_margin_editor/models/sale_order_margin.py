# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api, fields
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
    margin_switch_method = fields.Selection(selection=[
        ('Percent', _('Percent')),
        ('Monetary', _('Monetary')),
    ], string='Switch Method Margin', default='Percent', required=True)

    @api.onchange('margin_global_edit')
    def margin_monetary_change(self):
        if self.margin_global_edit >= 100:
            self.margin_global_edit = 99.99
        elif self.margin_global_edit <= -100:
            self.margin_global_edit = -99.99

        self.margin_global_product = self.margin_global_edit
        self.margin_product_edit_change(ignore_update_sale_margin=True)
        self.margin_global_service = self.margin_global_edit
        self.margin_service_edit_change(ignore_update_sale_margin=True)
        self._product_margin()

    @api.onchange('margin_global_product')
    def margin_product_edit_change(self, ignore_update_sale_margin=False):
        if self.margin_global_product >= 100:
            self.margin_global_product = 99.99
        elif self.margin_global_product <= -100:
            self.margin_global_product = -99.99

        has_change = False
        for line in self.order_line:
            if line.product_id.type != "service" and not line.margin_lock:
                self._update_line_margin_monetary(line, self.margin_global_product)
                has_change = True
        if not ignore_update_sale_margin and has_change:
            self._product_margin()

    @api.onchange('margin_global_service')
    def margin_service_edit_change(self, ignore_update_sale_margin=False):
        if self.margin_global_service >= 100:
            self.margin_global_service = 99.99
        elif self.margin_global_service <= -100:
            self.margin_global_service = -99.99

        has_change = False
        for line in self.order_line:
            if line.product_id.type == "service" and not line.margin_lock:
                self._update_line_margin_monetary(line, self.margin_global_service)
                has_change = True
            if not ignore_update_sale_margin and has_change:
                self._product_margin()

    def _update_line_margin_monetary(self, line, marge):
        marge_percent = marge / 100
        if line.purchase_price:
            if marge_percent != 1:
                line.margin_monetary = (marge_percent * line.purchase_price) / (
                    1 - marge_percent)
                line.margin_percent_edit = marge_percent * 100.
            else:
                line.margin_monetary = 0
                line.margin_percent_edit = 0
        else:
            line.margin_monetary = marge_percent
        line.price_unit = line.purchase_price + line.margin_monetary


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_monetary = fields.Float(string="Margin ($)",
                                   digits=dp.get_precision('Product Price'))

    margin_lock = fields.Boolean(string="Lock margin", default=False,
                                 help="Don't be affected by global margin.")

    margin_percent_edit = fields.Float(string="Margin (%)")

    @api.onchange('purchase_price')
    def margin_purchase_price_change(self):
        if self.order_id.margin_switch_method == 'Percent':
            # Percent
            if self.margin_lock:
                if not self.price_unit:
                    margin_percent = 0
                else:
                    margin_percent = (self.margin_monetary / self.price_unit)
            else:
                if self.product_id.type == "service":
                    margin_percent = self.order_id.margin_global_service / 100
                else:
                    margin_percent = self.order_id.margin_global_product / 100
            self.price_unit = self._price_unit_calc(margin_percent, self.purchase_price)
        elif self.order_id.margin_switch_method == 'Monetary':
            # Monetary
            self.price_unit = self.purchase_price + self.margin_monetary
        else:
            raise ValueError(_("Unknown value of margin_switch_method"))

    @api.onchange('margin_percent_edit')
    def margin_percent_edit_change(self):
        self.price_unit = self._price_unit_calc(self.margin_percent_edit / 100,
                                                self.purchase_price)

    @api.onchange('margin_percent')
    def margin_percent_change(self):
        self.margin_percent_edit = self.margin_percent

    @api.onchange('margin_monetary')
    def margin_monetary_change(self):
        self.price_unit = self.purchase_price + self.margin_monetary
        self._product_margin()

    @api.onchange('price_unit')
    def price_unit_margin_change(self):
        self.margin_monetary = self.price_unit - self.purchase_price

    @staticmethod
    def _price_unit_calc(margin_percent, purchase_price):
        if not margin_percent:
            return 0.
        if margin_percent == 1:
            margin_percent = 0.9999999
        new_margin_monetary = (margin_percent * purchase_price) / (1 - margin_percent)
        return new_margin_monetary / margin_percent

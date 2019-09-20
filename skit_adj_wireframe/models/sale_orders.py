# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_round, float_repr
from datetime import timedelta



class SkitError(models.Model):
    _name = 'skit.error'

    @api.multi
    def skit_warn(self):
        return


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nick_name = fields.Char(string="Nick Name")
    customer_items = fields.Char(string="Customer Item #")
    contract_no = fields.Char(string="Contract No.")
    ship_from = fields.Many2one('stock.warehouse', string="Ship From")
    ship_not_later = fields.Datetime(string="Ship Not Later")
    ship_not_before = fields.Datetime(string="Ship Not Before")
    warehouse_contact = fields.Many2one('res.users',
                                        string="Warehouse Contact")
    distribution_center = fields.Many2one('stock.warehouse',
                                          string="Distribution Center")
    location_id = fields.Many2one('stock.location', string="Location")
    order_contract = fields.Char(string="Order Contract")
    consolidator = fields.Char(string="Consolidator")
    internal_item_no = fields.Char(string="Internal Item No.")
    line_description = fields.Char(string="Line Description")
    fob_description = fields.Char(string="FOB/Description")
    promo_deal_no = fields.Char(string="Promotional/Deal No.")
    request_delivery_date = fields.Datetime(string="Request Delivery Date")
    weight = fields.Float(string="Weight(Ibs)")
    height = fields.Float(string="Height(Feet)")
    allowance_percent = fields.Float(string="Allowance Percent")
    allowance_description = fields.Char(string="Allowance Description")
    remark = fields.Text(string='Remarks', help="Notes/Remark")
    description = fields.Text("Description")
    sale_duty = fields.Char("Duty$")
    freight_cuft = fields.Float("Freight per Cu Ft", default="3")

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        availabiltity = False
        current_date = fields.Date.from_string(fields.Date.today())
        w_cm = 0
        d_cm = 0
        h_cm = 0
        weight = 0
        for picking in self.picking_ids:
            for mline in picking.move_lines:
                w_cm += (mline.product_id.carton_w_cm * mline.product_uom_qty)
                d_cm += (mline.product_id.carton_d_cm * mline.product_uom_qty)
                h_cm += (mline.product_id.carton_h_cm * mline.product_uom_qty)
                weight += (mline.product_id.item_weight * mline.product_uom_qty)
                if(mline.product_uom_qty > mline.reserved_availability):
                    availabiltity = True
            carton_cm = (w_cm * d_cm * h_cm)
            cubic_feet = (carton_cm / 28316.846592)
            picking.update({'carton_w_cm': w_cm,
                            'carton_d_cm': d_cm,
                            'carton_h_cm': h_cm,
                            'cu_ft': cubic_feet,
                            'weight': weight})
            if(not availabiltity):
                picking.delivery_date = current_date
                picking.so_release_target = current_date
                picking.sa_release_target = current_date - timedelta(days=2)
                picking.qaa_date = current_date - timedelta(days=4)
                picking.inspection_date = current_date - timedelta(days=7)
                picking.safety_complete = current_date - timedelta(days=12)
                picking.book_by_date = current_date - timedelta(days=14)
                picking.dupro_date = current_date - timedelta(days=21)
                picking.sample_collection = current_date - timedelta(days=21)
                picking.sample_selling = current_date - timedelta(days=35)
                picking.po_date_receipt = current_date - timedelta(days=56)
                picking.po_good_through = current_date + timedelta(days=9)
                picking.start_ship_window = current_date + timedelta(days=14)
                picking.lsd = current_date + timedelta(days=28)


class SkitSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_templ_id = fields.Many2one('product.template',
                                       related="product_id.product_tmpl_id")

    def change_unit_price(self, price_unit, product):
        products = self.env['product.product'].search([('id', '=', product)])
        margin = products.gross_margin
        prec = self.env['decimal.precision'].precision_get('Product Price')
        cost = (price_unit-products.standard_price)
        price = ((cost)/products.standard_price)
        tot_price = (price*100)
        tot_amount = float_repr(float_round(tot_price, precision_digits=prec), precision_digits=prec)
        if float(tot_amount) < margin:
            return False
        else:
            return True

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

    client_order_ref = fields.Char(string='Customer Order Number',
                                   copy=False)
    nick_name = fields.Char(string="Nick Name")
    customer_items = fields.Char(string="Customer Item #")
    contract_no = fields.Char(string="Contract No.")
    ship_from = fields.Many2one('stock.warehouse', string="Ship From")
    ship_not_later = fields.Date(string="Ship Not Later/LSD")
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
    weight = fields.Float(string="Weight(Ibs)",digits=dp.get_precision('Product Price'))
    height = fields.Float(string="Height(Feet)")
    allowance_percent = fields.Float(string="Allowance Percent")
    allowance_description = fields.Char(string="Allowance Description")
    remark = fields.Text(string='Remarks', help="Notes/Remark")
    description = fields.Text("Description")
    sale_duty = fields.Char("Duty$")
    freight_cuft = fields.Float("Freight per Cu Ft", default="3")
    sa_frieght = fields.Datetime("SA Frieght")
    cfs_cut_off = fields.Date("CFS/CY Cutoff")
    in_pl = fields.Char("In & PL")

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        availabiltity = False
        current_date = fields.Date.from_string(fields.Date.today())
        w_cm = 0
        d_cm = 0
        h_cm = 0
        weight = 0
        prec = self.env['decimal.precision'].precision_get('Product Price')
        for picking in self.picking_ids:
            for mline in picking.move_lines:
                w_cm += (mline.product_id.carton_w_cm * mline.product_uom_qty)
                d_cm += (mline.product_id.carton_d_cm * mline.product_uom_qty)
                h_cm += (mline.product_id.carton_h_cm * mline.product_uom_qty)
                weight += (mline.product_id.item_weight * mline.product_uom_qty)
                # if(mline.product_uom_qty > mline.reserved_availability):
                    # availabiltity = True
            carton_cm = (w_cm * d_cm * h_cm)
            cubic_feet = (carton_cm / 28316.846592)
            cubicfeet = float_repr(float_round(cubic_feet, precision_digits=prec),precision_digits=prec)
            tot_weight = float_repr(float_round(weight, precision_digits=prec),precision_digits=prec)
            picking.update({
                'customer_order_no': self.client_order_ref,
                'carton_w_cm': w_cm,
                'carton_d_cm': d_cm,
                'carton_h_cm': h_cm,
                'cu_ft': cubicfeet,
                'weight': tot_weight
            })
            # if(not availabiltity):
                # picking.delivery_date = current_date
                # picking.so_release_target = current_date
                # picking.sa_release_target = current_date - timedelta(days=2)
                # picking.qaa_date = current_date - timedelta(days=4)
                # picking.inspection_date = current_date - timedelta(days=7)
                # picking.safety_complete = current_date - timedelta(days=12)
                # picking.book_by_date = current_date - timedelta(days=14)
                # picking.dupro_date = current_date - timedelta(days=21)
                # picking.sample_collection = current_date - timedelta(days=21)
                # picking.sample_selling = current_date - timedelta(days=35)
                # picking.po_date_receipt = current_date - timedelta(days=56)
                # picking.po_good_through = current_date + timedelta(days=9)
                # picking.start_ship_window = current_date + timedelta(days=14)
                # picking.lsd = current_date + timedelta(days=28)

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        current_date = fields.Date.from_string(fields.Date.today())
        order.ship_not_later = current_date
        order.cfs_cut_off = current_date - timedelta(days=19)
        return order

    @api.onchange('ship_not_later')
    def _onchange_ship_not_later(self):
        if self.ship_not_later:
            ship_not_later = fields.Date.from_string(self.ship_not_later)
            self.cfs_cut_off = ship_not_later - timedelta(days=19)

class SkitSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_templ_id = fields.Many2one('product.template',
                                       related="product_id.product_tmpl_id")
    upc_code_ids = fields.Many2many('product.attr.color',string='Colors UPC/APN')

    def change_unit_price(self, price_unit, product):
        products = self.env['product.product'].search([('id', '=', product)])
        margin = products.gross_margin
        prec = self.env['decimal.precision'].precision_get('Product Price')
        cost_price= products.standard_price
        if price_unit and cost_price:
            cost = (price_unit-cost_price)
            price = ((cost)/products.standard_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec), precision_digits=prec)
            if float(tot_amount) < margin:
                return False
            else:
                return True

    @api.onchange('product_id')
    def onchange_productid(self):
        product = self.product_id
        if product:
            self.upc_code_ids = [[6,0,product.product_attr_color_ids.ids]]

class SaleReport(models.Model):
    _inherit = "sale.report"

    port = fields.Char("Port", help="Shipping Port")
    client_order_ref = fields.Char(string='Customer PO', copy=False)
    fcr_no = fields.Char("FCR #")
    etd = fields.Char("ETD")
    adj_po  = fields.Char("ADJ PO")
    description_sale = fields.Char("Item Description")
    remark = fields.Char(string='Remarks', help="Notes/Remark")
    deadline_book = fields.Date("Deadline Booked")
    actual_booked_date = fields.Datetime("Actual Booked Date")
    received_date = fields.Datetime("SA Deadline")
    cargo_received_date = fields.Datetime("Cargo Received Date")
    actual_etd = fields.Datetime("Actual ETD")
    wpa_name = fields.Char("WBA PO")
    qtyopen = fields.Float("QTY Open")
    crd = fields.Char(string="Delivery By/CRD", help="CRD/DELIVERY DATE")
    sa_frieght = fields.Datetime("SA Frieght")
    cfs_cut_off = fields.Char("CFS Cut off")
    in_pl = fields.Char("In & PL")

    def _select(self):
        return super(SaleReport, self)._select() + ",s.remark as remark,s.client_order_ref as client_order_ref,t.port as port,t.description_sale as description_sale,ai.fcr_no as fcr_no,ai.etd as etd, ai.adj_po as adj_po, sp.deadline_book as deadline_book,\
                                                    sp.actual_booked_date as actual_booked_date,sp.received_date as received_date,sp.cargo_received_date as cargo_received_date,\
                                                    sp.actual_etd,po.crd as crd,po.name as wpa_name,((select sum(product_qty) from purchase_order_line where order_id = po.id ) - (select sum(qty_received) from purchase_order_line where order_id = po.id )) as qtyopen,\
                                                    s.sa_frieght as sa_frieght,s.cfs_cut_off as cfs_cut_off,s.in_pl as in_pl"

    def _from(self):
        return super(SaleReport, self)._from() + "left join account_invoice ai on (ai.origin = s.name)\
                                                left join stock_picking sp on (sp.origin = s.name)\
                                                inner join stock_move sm on sp.id = sm.picking_id\
                                                left outer join purchase_request_line prl on sm.id = prl.move_id\
                                                left outer join purchase_request pr on prl.request_id = pr.id\
                                                left outer join purchase_order_line pol on prl.purchase_line_id = pol.id\
                                                left outer join purchase_order po on pol.order_id = po.id"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ",s.remark,s.client_order_ref,t.port,t.description_sale,ai.fcr_no,ai.etd, ai.adj_po,sp.deadline_book,sp.actual_booked_date,sp.received_date,sp.cargo_received_date,sp.actual_etd,\
                                                    po.name,po.id,po.crd,s.sa_frieght,s.cfs_cut_off,s.in_pl"

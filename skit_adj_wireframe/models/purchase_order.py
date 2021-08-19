# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from logging import getLogger
from odoo import fields, models, api,  _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


def log(*to_output):
    getLogger().info('\n\n\n%s\n\n', to_output)


class SkitPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vendor_nickname = fields.Char(string="Vendor Nick Name")
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country',
                                 ondelete='restrict')
    contact_name = fields.Char('Vendor Contact Name')
    contact_email = fields.Char('Vendor Contact Email')
    po_good_through = fields.Date(string="PO Good Through")
    sample_sealing = fields.Date(string="Sample Sealing")
    sample_sealing_approval = fields.Date(string="Sample Sealing Approval")
    dupro_date = fields.Date(string="Dupro Date")
    pac_test_expiry = fields.Date(string="Pac Test Expiry")
    qaa_expiry = fields.Date(string="QAA Expiry")
    so_number = fields.Char(string="SO Number")
    sale_order_state = fields.Selection([
                                ('open', _('Open')),
                                ('closed', _('Closed'))], string='Sale Order State')
    sale_order_date = fields.Date(string="Sale Order Date")
    start_ship_window = fields.Date(string="Start of Ship Window")
    lsd = fields.Date(string="LSD", help="Sail by date / last ship date")
    ttl_carton = fields.Char(string="TTl Cartons", help="Carton Quantity")
    fcr_confirm = fields.Char(string="FCR Confirmed")
    sail_window_end = fields.Char(string="Sail Window End")

    book_by = fields.Date(string="Book By", compute="_compute_dates")

    @api.depends('lsd')
    def _compute_dates(self):
        config = self.env['skit.date.config'].search([])

        if config:
            config = config[0]

            for rec in self:
                if rec.lsd:
                    rec.book_by = (datetime.strptime(rec.lsd, "%Y-%m-%d")
                                   - timedelta(days=config.book_by_date))

    inspection_by = fields.Date(string="Inspection By")
    actual_inspection_date = fields.Date(string="Actual Inspection Date")
    sa_release = fields.Char(string="SA Release")
    so_release = fields.Char(string="SO Release")
    el_received = fields.Date(string="EI Received ")
    distribution_center = fields.Char(string="Distribution Center")
    acutal_booking = fields.Char(string="Acutal Booking")
    booking_number = fields.Char(string="Booking Number")
    begin_deliver_window = fields.Char(string="Begin of Deliver Window")
    freight_avail = fields.Char(string="Freight Avail")
    crd = fields.Char(string="CRD", help="CRD/DELIVERY DATE")
    sail_window_start = fields.Char(string="Sail Window Start")
    remark = fields.Text(string='Remarks', help="Notes/Remark")
    master_carton_total = fields.Char(string="Master Carton Total",
                                      help="Total Number of Master Cartons")
    total_cbm = fields.Char("Total CBM")
    description = fields.Text("Description")
    ship_via = fields.Many2one('skit.ship.via', "Ship Via")

    @api.onchange('partner_id')
    def _onchange_partner(self):
        partner = self.partner_id
        self.street = partner.street
        self.street2 = partner.street2
        self.zip = partner.zip
        self.city = partner.city
        self.state_id = partner.state_id.id
        self.country_id = partner.country_id.id


class skitPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    upc_code = fields.Many2many('product.attr.color',string='Colors UPC')
    cbm_per_case = fields.Char(string="CBM Per Carton")
    case_pack = fields.Char(string="Case Pack")
    qty_carton = fields.Integer(related="product_id.qty_master")
    ttl_carton = fields.Float(string="TTL Carton",
                              compute="_compute_ttl_carton",
                              digits=(12, 4))
    ttl_cbm = fields.Float(string="TTL CBM",
                           compute="_compute_ttl_cbm",
                           digits=(12, 4))

    @api.depends('ttl_carton')
    def _compute_ttl_cbm(self):
        for rec in self:
            rec.ttl_cbm = rec.ttl_carton * float(rec.cbm_per_case)

    @api.depends('qty_carton', 'product_qty')
    def _compute_ttl_carton(self):
        for rec in self:
            rec.ttl_carton = (float(rec.product_qty)
                              / rec.qty_carton if rec.qty_carton else 0)

    @api.onchange('product_id')
    def onchange_product_id(self):
        product = self.product_id
        super(skitPurchaseOrderLine, self).onchange_product_id()
        if product:
            self.name = product.description
            self.cbm_per_case = product.cbm
            self.case_pack = product.case_pack
            self.upc_code = [[6,0,product.product_attr_color_ids.ids]]

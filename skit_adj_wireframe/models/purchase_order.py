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
    start_ship_window = fields.Date(string="Start of Ship Window",
                                    compute="_compute_dates")
    lsd = fields.Date(string="LSD", help="Sail by date / last ship date")
    ttl_carton = fields.Char(string="TTl Cartons", help="Carton Quantity")
    fcr_confirm = fields.Char(string="FCR Confirmed")
    sail_window_end = fields.Char(string="Sail Window End")
    book_by = fields.Date(string="Book By", compute="_compute_dates")

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
                if not pickings:
                    res = order._prepare_picking()

                    res['lsd'] = datetime.strptime(order.lsd,
                                                   "%Y-%m-%d")
                    res['po_good_through'] = datetime.strptime(order.po_good_through,
                                                               "%Y-%m-%d")
                    res['start_ship_window'] = datetime.strptime(order.start_ship_window,
                                                                 "%Y-%m-%d")
                    res['book_by_date'] = datetime.strptime(order.book_by,
                                                            "%Y-%m-%d")
                    res['inspection_date'] = datetime.strptime(order.inspection_by,
                                                               "%Y-%m-%d")
                    res['sa_release_target'] = datetime.strptime(order.sa_release,
                                                                 "%Y-%m-%d")
                    res['so_release_target'] = datetime.strptime(order.so_release,
                                                                 "%Y-%m-%d")

                    picking = StockPicking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.depends('lsd')
    def _compute_dates(self):
        config = self.env['skit.date.config'].search([])

        if config:
            config = config[0]

            for rec in self:
                if rec.lsd:
                    date_format = datetime.strptime(rec.lsd, "%Y-%m-%d")

                    if config.book_by_date:
                        rec.book_by = (date_format
                                       - timedelta(days=config.book_by_date))
                    if config.inspection_date:
                        rec.inspection_by = (date_format
                                             - timedelta(days=config.inspection_date))
                    if config.sa_release_target:
                        rec.sa_release = (date_format
                                          - timedelta(days=config.sa_release_target))
                    if config.so_release_target:
                        rec.so_release = (date_format
                                          - timedelta(days=config.so_release_target))
                    if config.start_ship_window:
                        rec.start_ship_window = (date_format
                                                 - timedelta(days=config.start_ship_window))
                    rec.crd = (date_format
                               - timedelta(days=19))

    inspection_by = fields.Date(string="Inspection By", compute="_compute_dates")
    actual_inspection_date = fields.Date(string="Actual Inspection Date")
    sa_release = fields.Date(string="SA Release", compute="_compute_dates")
    so_release = fields.Date(string="SO Release", compute="_compute_dates")
    el_received = fields.Date(string="EI Received ")
    distribution_center = fields.Char(string="Distribution Center")
    acutal_booking = fields.Char(string="Actual Booking")
    booking_number = fields.Char(string="Booking Number")
    begin_deliver_window = fields.Char(string="Begin of Deliver Window")
    freight_avail = fields.Char(string="Freight Avail")
    crd = fields.Date(string="CRD", help="CRD/DELIVERY DATE",
                      compute="_compute_dates")
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

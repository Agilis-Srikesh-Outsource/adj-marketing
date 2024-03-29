# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from odoo import fields, models, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools import float_round, float_repr
from odoo.addons import decimal_precision as dp


class Picking(models.Model):
    _inherit = "stock.picking"

    customer_order_no = fields.Char('Customer Order No.')
    delivery_date = fields.Date('Delivery Date',
                                copy=False,
                                index=True, readonly=False, store=True,
                                track_visibility='onchange',
                                help="Delivery Date of Transfer")
    show_request = fields.Boolean('Purchase Request', default=False)
    purchase_request_id = fields.One2many('purchase.request', 'picking_id',
                                          string='Purchase Request', copy=True)
    deadline_book = fields.Date("Deadline Booked")
    actual_booked_date = fields.Datetime("Actual Booked Date")
    received_date = fields.Datetime("SA Deadline/Received Date")
    cargo_received_date = fields.Datetime("Cargo Received Date")
    actual_etd = fields.Datetime("Actual ETD")
    origin_location = fields.Many2one('stock.location', "Origin Location")
    shipment_ref = fields.Char("Shipment Reference")
    lsd = fields.Date(string="LSD", help="Last ship date")
    start_ship_window = fields.Date(string="Start of Ship Window")
    po_good_through = fields.Date(string="PO Good Through",
                                  help="Carols CRD/PO Good Through")
    sa_release_target = fields.Date(string="SA Release Target")
    so_release_target = fields.Date(string="SO Release Target")
    qaa_date = fields.Date("QAA Date")
    inspection_date = fields.Date("Inspection Date")
    safety_complete = fields.Date("Safety Completed")
    book_by_date = fields.Date("Book By Date")
    dupro_date = fields.Date("Dupro Date")
    sample_collection = fields.Date("Sample Collection")
    sample_selling = fields.Date("Sample Selling")
    po_date_receipt = fields.Date("PO Date Receipt")
    carton_w_cm = fields.Float("Carton W (cm)",digits=dp.get_precision('Product Price'))
    carton_d_cm = fields.Float("Carton D (cm)",digits=dp.get_precision('Product Price'))
    carton_h_cm = fields.Float("Carton H (cm)",digits=dp.get_precision('Product Price'))
    cu_ft = fields.Float(string="CU Ft", help="Master Carton CU FT",digits=dp.get_precision('Product Price'))
    factory = fields.Char(string="Factory")
    fcr_no  = fields.Char("FCR")

    adj_po  = fields.Char("ADJ PO ")
    so_number = fields.Char("SO #")
    wic_number = fields.Char("WIC #")
    item_description = fields.Char("Item Description")
    case_pack = fields.Char(string="Case Pack")
    pieces_ordered = fields.Char(string="Pieces Ordered")
    quantity = fields.Integer(string="Quantity(carton)")
    fob_cost = fields.Char(string="FOB Cost/Price")
    total_po_cost = fields.Char(string="Total Po Cost")
    shipping_window_start = fields.Date(string="Shipping Window Start")
    shipping_window_end = fields.Date(string="Shipping Window End")
    port = fields.Char("Port", help="Shipping Port")
    remark = fields.Text(string='Remarks',help="Notes/Remark")


#     @api.depends('sale_id.confirmation_date')
#     @api.one
#     def _compute_delivery_date(self):
#         """ Delivery date based on Order confirmation date
#         and Product Lead Time(Max time for orderlines) """
#
#         if self.sale_id:
#             if(self.sale_id.confirmation_date):
#                 product_tmpl_ids = []
#                 sale_lead = []
#                 lead_day = 0
#                 for line in self.sale_id.order_line:
#                     product_tmpl_ids.append(line.product_id.product_tmpl_id.id)
#                     sale_lead.append(line.id)
#                 sale_line = self.env['sale.order.line'].sudo().search([('id', 'in', sale_lead), ('customer_lead', '!=', False)],
#                                                                       order='customer_lead DESC', limit=1)
#                 product_tmpl = self.env['product.template'].sudo().search([
#                     ('id', 'in', product_tmpl_ids), ('lead_time', '!=', False)], order='lead_time DESC',
#                     limit=1)
#                 if(sale_line) and sale_line.customer_lead:
#                     lead_day = int(sale_line.customer_lead)
#                 else:
#                     if(product_tmpl) and product_tmpl.lead_time:
#                         lead_day = int(product_tmpl.lead_time)
#                 confirm_date_time = datetime.strptime(
#                     self.sale_id.confirmation_date,
#                     DEFAULT_SERVER_DATETIME_FORMAT)
#                 lead_day = confirm_date_time + timedelta(days=lead_day)
#                 confirm_date = lead_day.date()
#                 self.delivery_date = confirm_date
#         else:
#             self.delivery_date = self.delivery_date

    @api.multi
    def action_assign(self):
        super(Picking, self).action_assign()
        if self.env.context.get('is_check_quant', False):
            purchase_request = False
            for mline in self.move_lines:
                if(mline.product_uom_qty > mline.reserved_availability):
                    purchase_request = True
                    mline.write({'is_check_availability': True})
                else:
                    mline.write({'is_check_availability': False})
            if(purchase_request):
                self.write({'show_request': True})
                return {
                        'type': 'ir.actions.act_window',
                        'name': 'Warning',
                        'res_model': 'delivery.warning.wizard',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'view_id': self.env.ref('skit_adj_wireframe.view_delivery_warning_wizard',False).id,
                        'target': 'new',
                }
        return True

    @api.multi
    def action_purchase_request(self):
        """ Create a Purchase Request """
        if not self.purchase_request_id:
            type_obj = self.env['stock.picking.type']
            company_id = self.env.user.company_id.id
            type = type_obj.search([('code', '=', 'incoming'),
                                    ('warehouse_id.company_id', '=', company_id)], limit=1)
            if not type:
                type = type_obj.search([('code', '=', 'incoming'),
                                        ('warehouse_id', '=', False)], limit=1)
            request = self.env['purchase.request'].sudo().create({
                'requested_by': self.env.uid,
                'picking_type_id': type.id,
                'picking_id': self.id})
            request_line = self.env['purchase.request.line']
            for mline in self.move_lines:
                if(mline.product_uom_qty > mline.reserved_availability):
                    name = mline.product_id.name
                    if mline.product_id.code:
                        name = '[%s] %s' % (name, mline.product_id.code)
                    if mline.product_id.description_purchase:
                        name += '\n' + mline.product_id.description_purchase
                    qty = mline.product_uom_qty - mline.reserved_availability
                    current_date = datetime.strptime(fields.Date.today(), DEFAULT_SERVER_DATE_FORMAT)
                    request_line.create({'product_id': mline.product_id.id,
                                         'product_qty': qty,
                                         'name': name,
                                         'product_uom_id': mline.product_id.uom_id.id,
                                         'date_required': current_date,
                                         'request_id': request.id,
                                         'move_id': mline.id})

        if self.purchase_request_id:
            request_id = self.purchase_request_id[0].id
        else:
            request_id = self.purchase_request_id.id
        return {
            'name': _('Request Form'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'res_id': request_id,
            'view_id': self.env.ref('skit_po_request.view_purchase_request_form').id,
            'type': 'ir.actions.act_window',
            'context': {'default_picking_id': self.id}
        }

    # @api.multi
    # def button_validate(self):
        # current_date = fields.Date.from_string(fields.Date.today())
        # purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
        # if purchase_order:
            # pr_lines = self.env['purchase.request.line'].search([('purchase_id','=',purchase_order.id)])
            # for pr_line in pr_lines:
                # move_id = pr_line.move_id
                # if move_id:
                    # picking_id = move_id.picking_id
                    # if picking_id:
                        # picking_id.po_date_receipt = current_date
                        # picking_id.sample_selling = current_date + timedelta(days=21)
                        # picking_id.sample_collection = current_date + timedelta(days=35)
                        # picking_id.dupro_date = current_date + timedelta(days=35)
                        # picking_id.book_by_date = current_date + timedelta(days=42)
                        # picking_id.safety_complete = current_date + timedelta(days=44)
                        # picking_id.inspection_date = current_date + timedelta(days=49)
                        # picking_id.qaa_date = current_date + timedelta(days=52)
                        # picking_id.sa_release_target = current_date + timedelta(days=54)
                        # picking_id.so_release_target = current_date + timedelta(days=56)
                        # picking_id.delivery_date = current_date + timedelta(days=56)
                        # picking_id.po_good_through = current_date + timedelta(days=65)
                        # picking_id.start_ship_window = current_date + timedelta(days=70)
                        # picking_id.lsd = current_date + timedelta(days=84)
                        #
        # return super(Picking, self).button_validate()

    @api.onchange('carton_w_cm', 'carton_d_cm', 'carton_h_cm')
    def _onchange_cu_ft(self):
        prec = self.env['decimal.precision'].precision_get('Product Price')
        carton_cm = (self.carton_d_cm * self.carton_h_cm * self.carton_w_cm)
        cubic_feet = (carton_cm / 28316.846592)
        cubicfeet = float_repr(float_round(cubic_feet, precision_digits=prec),precision_digits=prec)
        self.update({'cu_ft': cubicfeet})

    @api.onchange('lsd')
    def _onchange_lsd_date(self):
        date_config = self.env['skit.date.config'].search([],limit=1)
        if self.lsd:
            lsd = fields.Date.from_string(self.lsd)
            self.start_ship_window = lsd - timedelta(days=date_config.start_ship_window)
            self.po_good_through = lsd - timedelta(days=date_config.po_good_through)
            self.delivery_date = lsd - timedelta(days=date_config.delivery_date)
            self.so_release_target = lsd - timedelta(days=date_config.so_release_target)
            self.sa_release_target = lsd - timedelta(days=date_config.sa_release_target)
            self.qaa_date = lsd - timedelta(days=date_config.qaa_date)
            self.inspection_date = lsd - timedelta(days=date_config.inspection_date)
            self.safety_complete = lsd - timedelta(days=date_config.safety_complete)
            self.book_by_date = lsd - timedelta(days=date_config.book_by_date)
            self.dupro_date = lsd - timedelta(days=date_config.dupro_date)
            self.sample_collection = lsd - timedelta(days=date_config.sample_collection)
            self.sample_selling = lsd - timedelta(days=date_config.sample_selling)
            self.po_date_receipt = lsd - timedelta(days=date_config.po_date_receipt)

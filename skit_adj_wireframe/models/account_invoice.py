# -*- coding: utf-8 -*-

from odoo import fields, models,_


class SkitAccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    nick_name = fields.Char("Nick Name")
    page = fields.Char(string="Page")
    ship_to = fields.Char(string="Ship To")
    shipping_method = fields.Many2one('delivery.carrier',string="Shipping Method")
    ship_date = fields.Date(string="Ship Date")
    freight = fields.Char(string="Freight")
    credit_memo_no = fields.Char(string="Check/Credit Memo No.")
    so_number = fields.Char("SO Number")
    master_carton_total = fields.Char(string="Master Carton Total",help="Total Number of Master Cartons")
    total_cbm = fields.Char("Total CBM")
    deffective_allowance = fields.Char("Deffective allowance")
    booking_inv = fields.Char("Booking/Commercial inv")
    adj_invoice = fields.Char("ADJ Invoice")
    total_net_weight = fields.Float("Total net weight")
    fcr_no  = fields.Char("FCR #")
    etd  = fields.Char("ETD")
    fcr_confirmed  = fields.Char("FCR Confirmed")
    original_fcr_receive = fields.Char("Original FCR Received")
    sail_window  = fields.Char("Sail Window")
    local_charge  = fields.Char("Local Charges")
    remark = fields.Text(string='Remarks',help="Notes/Remark")
    shipping_port = fields.Char("Port",help="Shipping Port")
    retail_item = fields.Char("Retail Item #",help="Customer Item #")
    delivery_date =fields.Date(string="Delivery Date", help="CRD/Delivery Date")
    order_total = fields.Float("Order total $",help="Total  value of Purchase order")
    adj_po  = fields.Char("ADJ PO #") 
    custom = fields.Char("Customs")
    package_cost = fields.Float("Packaging Costs")
    deposit = fields.Float("Deposit $")
    deposit_date = fields.Date("Deposit Date")
    final_payment = fields.Float("Final payment $")
    final_payment_date = fields.Date("Final payment Date")
    invoice = fields.Char("Invoice#")
    complete = fields.Selection([
                                ('yes', _('Yes')),
                                ('no', _('No'))], string='Complete')


class SkitAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    sell_price = fields.Float("Sell Price")


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    cost_price = fields.Float('Cost($)', readonly=True)
    gross_profit_amt = fields.Float('Gross Profit($)', readonly=True)
    gross_profit_precent = fields.Float('Gross Profit(%)', readonly=True, group_operator = 'avg')
    product_qty = fields.Float(string='Unit Sold', readonly=True)
    price_total = fields.Float(string='Sales($)', readonly=True)
    item_id = fields.Integer('Item ID', readonly=True)
    item_description = fields.Char('Item Description', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.cost_price as cost_price, sub.gross_profit_amt as gross_profit_amt, sub.gross_profit_precent as gross_profit_precent, sub.item_id as item_id, sub.item_description as item_description"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", (ip.value_float * ail.quantity) as cost_price, (SUM(ail.price_subtotal_signed * invoice_type.sign) - (ip.value_float * ail.quantity)) as gross_profit_amt, (MAX((ail.price_subtotal_signed * invoice_type.sign) - (ip.value_float * ail.quantity))/(ip.value_float * ail.quantity))*100 as gross_profit_precent, pt.item_no as item_id, pt.item_description as item_description"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ip.value_float, pt.item_no, pt.item_description"

    def _from(self):
        return super(AccountInvoiceReport, self)._from() + " LEFT JOIN ir_property ip ON (ip.name='standard_price' AND ip.res_id=CONCAT('product.product,',pr.id) AND ip.company_id=ai.company_id)"

 
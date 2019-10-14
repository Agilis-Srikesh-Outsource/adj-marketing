# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_round, float_repr
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cu_ft = fields.Float(string="CU FT", help="Master Carton CU FT")
   # buy_price = fields.Float('Buy Price',
   #                          digits=dp.get_precision('Product Price'))
    sell_price = fields.Float('Sell Price1',
                              digits=dp.get_precision('Product Price'))
    sell_price2 = fields.Float('Sell Price2',
                               digits=dp.get_precision('Product Price'))
    sell_price3 = fields.Float('Sell Price3',
                               digits=dp.get_precision('Product Price'))
    factory_items = fields.Char(string="Factory Item #")
    adj_items = fields.Char(string="ADJ Retail Number")
    retail_items = fields.Char(string="Retail Number #")
    hts = fields.Char(string="HTS #", help="Import Code")
    duty = fields.Float('Duty %')
    import_val = fields.Selection([
                                ('yes', _('Yes')),
                                ('no', _('No'))], string='Import')
    status = fields.Selection([
                                ('live', _('Live')),
                                ('discontinued', _('Discontinued')),
                                ('quote', _('Quote'))], string='Status')
    qty_inner = fields.Integer("QTY Inner", help="Quantity in inner carton")
    qty_master = fields.Integer("QTY Master",
                                help="Quantity  in shipping carton")
    pdq = fields.Selection([
                            ('yes', _('Yes')),
                            ('no', _('No'))], string='PDQ')
    item_weight = fields.Float("Item Weight KG")
    carton_weight = fields.Float("Carton Weight KG")
    item_w_cm = fields.Float("Item W (cm)")
    item_d_cm = fields.Float("Item D (cm)")
    item_h_cm = fields.Float("Item H (cm)")
    carton_w_cm = fields.Float("Carton W (cm)")
    carton_d_cm = fields.Float("Carton D (cm)")
    carton_h_cm = fields.Float("Carton H (cm)")
    carton_w_in = fields.Float("Carton W (in)")
    carton_d_in = fields.Float("Carton D (in)")
    carton_h_in = fields.Float("Carton H (in)")
    cbm = fields.Float("CBM", help="Master Carton Cube")
    gtin = fields.Char("GTIN")
    remark = fields.Text(string='Remarks', help="Notes/Remark")
    product_brand = fields.Char("Brand", help="Brand used on Product")
    landed_cost = fields.Char("ELC", help="Estimated Landed Cost")
    min_order_qty = fields.Char("MOQ", help="Minimum Order Quantity")
    lead_time = fields.Char("Lead Time")
    port = fields.Char("Port", help="Shipping Port")
    commission = fields.Float("Commision %", help="Sales Commision",
                              default=0.0)
    gross_margin = fields.Float("Gross Margin%", default=30)
    safty_test = fields.Date("Pre Production Safety Test")
    gmi = fields.Char("GMI")
    sample_sealing = fields.Date(string="Sample Sealing")
    sample_sealing_approval = fields.Date(string="Sample Sealing Approval")
    drop_test = fields.Char("Drop Test")
    sample_collection_test = fields.Date("Sample Collection",
                                         help="Sample collection for Test")
    pac_test_expiry = fields.Date("Pac Test Expiry")
    pac_certificate = fields.Char("Pac Certificate #")
    safety_test_report = fields.Char("Safety Test Report#")
    qaa_expiry = fields.Date("QAA Expiry")
    sale_order_line_ids = fields.One2many('sale.order.line',
                                          'product_templ_id', 'Sales Order')
    product_classification = fields.Many2one('product.classification',
                                             "Product Classification")
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        compute='_compute_list_price',
        readonly=False, store=True,
        help="Compute price based on Cost and Gross Margin values")
    
    @api.onchange('carton_w_cm', 'carton_d_cm', 'carton_h_cm')
    def _onchange_cu_ft(self):
        carton_cm = ((self.carton_d_cm * self.carton_h_cm * self.carton_w_cm)/1000000)
        carton_d_in = (self.carton_d_cm / 2.54)
        carton_h_in = (self.carton_h_cm / 2.54)
        carton_w_in = (self.carton_w_cm / 2.54)
        cubic_feet  = ((self.carton_d_in * self.carton_h_in * self.carton_w_in)/1728) 
        self.update({'cbm': carton_cm,
                     'carton_d_in': carton_d_in,
                     'carton_h_in': carton_h_in,
                     'carton_w_in': carton_w_in,
                     'cu_ft': cubic_feet})
#
    @api.onchange('carton_w_in', 'carton_d_in', 'carton_h_in')
    def _onchange_cu_ft_inches(self):
        carton_cm = (self.carton_d_in * self.carton_h_in * self.carton_w_in)
        carton_d_cm = (self.carton_d_in *  2.54)
        carton_h_cm = (self.carton_h_in *  2.54)
        carton_w_cm = (self.carton_w_in *  2.54)
        cubic_feet = (carton_cm / 1728)
        self.update({'carton_d_cm': carton_d_cm,
                     'carton_h_cm': carton_h_cm,
                     'carton_w_cm': carton_w_cm,
                     'cu_ft': cubic_feet})

    @api.onchange('sell_price')
    def onchange_sellprice(self):
        cost_price = self.standard_price
        sell_price = self.sell_price
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('sell_price2')
    def onchange_sellprice2(self):
        cost_price = self.standard_price
        sell_price = self.sell_price2
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('sell_price3')
    def onchange_sellprice3(self):
        cost_price = self.standard_price
        sell_price = self.sell_price3
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('standard_price')
    def onchage_cost_price(self):
        sellprice = self.sell_price
        sellprice2 = self.sell_price2
        sellprice3 = self.sell_price3
        costprice = self.standard_price
        values = []
        values.append({'sellprice': sellprice,
                       'name': 'Selling price 1'})
        values.append({'sellprice': sellprice2,
                       'name': 'Selling price 2'})
        values.append({'sellprice': sellprice3,
                       'name': 'Selling price 3'})
        for vals in values:
            if vals.get('sellprice') > 0:
                if((vals.get('sellprice') < costprice)):
                    raise UserError(_(vals.get('name')+' should not be lesser than Cost Price'))

    @api.depends('standard_price', 'gross_margin',)
    def _compute_list_price(self):
        """
        Compute Product's Sales Price based upon Cost and Gross Margin values.
        """
        for product in self:
            gross_margin_percent = ((product.gross_margin * product.standard_price) / 100)
            list_price = product.standard_price + gross_margin_percent
            product.list_price = list_price


class SkitProductProduct(models.Model):
    _inherit = "product.product"

    sale_order_line_ids = fields.One2many('sale.order.line', 'product_id',
                                          'Sales Order')

    @api.onchange('carton_w_cm', 'carton_d_cm', 'carton_h_cm')
    def _onchange_cu_ft(self):
        carton_cm = ((self.carton_d_cm * self.carton_h_cm * self.carton_w_cm)/1000000)
        carton_d_in = (self.carton_d_cm / 2.54)
        carton_h_in = (self.carton_h_cm / 2.54)
        carton_w_in = (self.carton_w_cm / 2.54)
        cubic_feet  = ((self.carton_d_in * self.carton_h_in * self.carton_w_in)/1728) 
        self.update({'cbm': carton_cm,
                     'carton_d_in': carton_d_in,
                     'carton_h_in': carton_h_in,
                     'carton_w_in': carton_w_in,
                     'cu_ft': cubic_feet})
    @api.onchange('carton_w_in', 'carton_d_in', 'carton_h_in')
    def _onchange_cu_ft_inches(self):
        carton_cm = (self.carton_d_in * self.carton_h_in * self.carton_w_in)
        carton_d_cm = (self.carton_d_in *  2.54)
        carton_h_cm = (self.carton_h_in * 2.54)
        carton_w_cm = (self.carton_w_in * 2.54)
        cubic_feet = (carton_cm / 1728)
        self.update({'carton_d_cm': carton_d_cm,
                     'carton_h_cm': carton_h_cm,
                     'carton_w_cm': carton_w_cm,
                     'cu_ft': cubic_feet})
        
    @api.onchange('sell_price')
    def onchange_sellprice(self):
        cost_price = self.standard_price
        sell_price = self.sell_price
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('sell_price2')
    def onchange_sellprice2(self):
        cost_price = self.standard_price
        sell_price = self.sell_price2
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('sell_price3')
    def onchange_sellprice3(self):
        cost_price = self.standard_price
        sell_price = self.sell_price3
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/cost_price)
            tot_price = (price*100)
            tot_amount = float_repr(float_round(tot_price, precision_digits=prec),precision_digits=prec)
            if float(tot_amount) < self.gross_margin:
                raise UserError(_('Sell price should not be lesser than Gross Margin %'))

    @api.onchange('standard_price')
    def onchage_cost_price(self):
        sellprice = self.sell_price
        sellprice2 = self.sell_price2
        sellprice3 = self.sell_price3
        costprice = self.standard_price
        values = []
        values.append({'sellprice': sellprice,
                       'name': 'Selling price 1'})
        values.append({'sellprice': sellprice2,
                       'name': 'Selling price 2'})
        values.append({'sellprice': sellprice3,
                       'name': 'Selling price 3'})
        for vals in values:
            if vals.get('sellprice') > 0:
                if((vals.get('sellprice') < costprice)):
                    raise UserError(_(vals.get('name')+' should not be lesser than Cost Price'))

    @api.onchange('standard_price', 'gross_margin')
    def compute_lst_price(self):
        """
        Compute Product's Sales Price based upon Cost and Gross Margin values.
        """
        for product in self:
            gross_margin_percent = ((product.gross_margin * product.standard_price) / 100)
            list_price = product.standard_price + gross_margin_percent
            product.lst_price = list_price


class ProductClassification(models.Model):
    _name = 'product.classification'
    _description = "Product Classification"

    name = fields.Char("Name")

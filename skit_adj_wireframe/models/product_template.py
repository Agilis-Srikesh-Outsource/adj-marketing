# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_round, float_repr
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cu_ft = fields.Float(string="CU FT", help="Master Carton CU FT",
                         digits=dp.get_precision('Product Price'))
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
    item_weight = fields.Float("Item Weight KG",digits=dp.get_precision('Product Price'))
    carton_weight = fields.Float("Carton Weight KG",digits=dp.get_precision('Product Price'))
    item_weight_lbs = fields.Float("Item Weight LBS",digits=dp.get_precision('Product Price'))
    carton_weight_lbs = fields.Float("Carton Weight LBS",digits=dp.get_precision('Product Price'))
    item_w_cm = fields.Float("Item W (cm)",digits=dp.get_precision('Product Price'))
    item_d_cm = fields.Float("Item D (cm)",digits=dp.get_precision('Product Price'))
    item_h_cm = fields.Float("Item H (cm)",digits=dp.get_precision('Product Price'))
    item_w_in = fields.Float("Item W (in)",digits=dp.get_precision('Product Price'))
    item_d_in = fields.Float("Item D (in)",digits=dp.get_precision('Product Price'))
    item_h_in = fields.Float("Item H (in)",digits=dp.get_precision('Product Price'))
    carton_w_cm = fields.Float("Carton W (cm)",digits=dp.get_precision('Product Price'))
    carton_d_cm = fields.Float("Carton D (cm)",digits=dp.get_precision('Product Price'))
    carton_h_cm = fields.Float("Carton H (cm)",digits=dp.get_precision('Product Price'))
    carton_w_in = fields.Float("Carton W (in)",digits=dp.get_precision('Product Price'))
    carton_d_in = fields.Float("Carton D (in)",digits=dp.get_precision('Product Price'))
    carton_h_in = fields.Float("Carton H (in)",digits=dp.get_precision('Product Price'))
    cbm = fields.Float("CBM", help="Master Carton Cube",digits=dp.get_precision('Product Price'))
    gtin = fields.Char("GTIN")
    remark = fields.Text(string='Remarks', help="Notes/Remark")
    product_brand = fields.Char("Brand", help="Brand used on Product")
    landed_cost = fields.Float("ELC",digits=dp.get_precision('Product Price'), help="Estimated Landed Cost")
    min_order_qty = fields.Char("MOQ", help="Minimum Order Quantity")
    lead_time = fields.Char("Lead Time")
    port = fields.Char("Port", help="Shipping Port")
    commission = fields.Float("Commision %", help="Sales Commision",
                              default=0.0)
    gross_margin = fields.Float("Gross Margin%")
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
    case_pack = fields.Float("Case Pack")
    material_const_finish = fields.Text("Material Construction Finish")
    packaging_id = fields.Many2one('product.packaging',"Packaging")
    duty_cost = fields.Float('Duty Cost $',digits=dp.get_precision('Product Price'))
    freight_rate_cuft = fields.Float('Freight rate per Cu.ft',digits=dp.get_precision('Product Price'))
    freight_unit = fields.Float('Freight per unit',digits=dp.get_precision('Product Price'))
    layer = fields.Integer("Layer")
    pallet = fields.Integer("Pallet")
    description_purchase = fields.Text(
        'Purchase Description', translate=True,related='remark',
        help="A description of the Product that you want to communicate to your vendors. "
             "This description will be copied to every Purchase Order, Receipt and Vendor Bill/Credit Note.")
    description_sale = fields.Text(
        'Sale Description', translate=True,related='remark',
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    product_attr_color_ids= fields.One2many('product.attr.color','product_id')
    
    @api.onchange('carton_w_cm', 'carton_d_cm', 'carton_h_cm')
    def _onchange_carton(self):
        group_carton = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_carton')
        group_cu_ft = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_cu_ft')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if float(group_carton)>0:
            carton_d_in = (float(self.carton_d_cm) * float(group_carton))
            self.carton_d_in = float_repr(float_round(carton_d_in, precision_digits=prec),precision_digits=prec)
            carton_h_in = (float(self.carton_h_cm) * float(group_carton))
            self.carton_h_in = float_repr(float_round(carton_h_in, precision_digits=prec),precision_digits=prec)
            carton_w_in = (float(self.carton_w_cm) * float(group_carton))
            self.carton_w_in = float_repr(float_round(carton_w_in, precision_digits=prec),precision_digits=prec)
            cbm = ((self.carton_d_cm * self.carton_h_cm * self.carton_w_cm)/1000000)
            self.cbm = float_repr(float_round(cbm, precision_digits=prec),precision_digits=prec)
        if float(group_cu_ft) > 0:
            cu_ft = (float(self.cbm) * float(group_cu_ft))
            self.cu_ft = float_repr(float_round(cu_ft, precision_digits=prec),precision_digits=prec)
            
    @api.onchange('item_w_cm', 'item_d_cm', 'item_h_cm')
    def _onchange_item(self):
        group_carton = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_carton')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if float(self.item_w_cm)>0 and float(group_carton):
            item_w_in = (float(self.item_w_cm) * float(group_carton))
            self.item_w_in = float_repr(float_round(item_w_in, precision_digits=prec),precision_digits=prec)
        if float(self.item_d_cm)>0 and float(group_carton):
            item_d_in = (float(self.item_d_cm) * float(group_carton))
            self.item_d_in = float_repr(float_round(item_d_in, precision_digits=prec),precision_digits=prec)
        if float(self.item_h_cm)>0 and float(group_carton):
            item_h_in = (float(self.item_h_cm) * float(group_carton))
            self.item_h_in = float_repr(float_round(item_h_in, precision_digits=prec),precision_digits=prec)
        
    @api.onchange('cbm')
    def _onchange_cbm(self):
        group_cu_ft = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_cu_ft')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if float(group_cu_ft) > 0:
            cu_ft = (float(self.cbm) * float(group_cu_ft))
            self.cu_ft = float_repr(float_round(cu_ft, precision_digits=prec),precision_digits=prec)
            
    @api.onchange('item_weight')
    def _onchange_weight(self):
        if self.item_weight > 0:
            self.item_weight_lbs = self.item_weight * 2.20462
        
        
    @api.onchange('carton_weight')
    def _onchange_cartonweight(self):
        if self.carton_weight > 0:
            self.carton_weight_lbs = self.carton_weight * 2.20462
            
    @api.onchange('standard_price','sell_price')
    def onchange_standard_price(self):
        cost_price = self.standard_price
        sell_price = self.sell_price
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and cost_price:
            cost = (sell_price-cost_price)
            price = ((cost)/sell_price)
            self.gross_margin = float_repr(float_round(price, precision_digits=prec),precision_digits=prec)
    
    @api.onchange('duty_cost','sell_price','freight_unit')
    def onchange_elc(self):
        sell_price = self.sell_price
        duty_cost = self.duty_cost
        freight_unit = self.freight_unit
        prec = self.env['decimal.precision'].precision_get('Product Price')
        elc = (sell_price+duty_cost+freight_unit)
        self.landed_cost = float_repr(float_round(elc, precision_digits=prec),precision_digits=prec)
            
    @api.onchange('cu_ft','freight_rate_cuft','qty_master')
    def onchange_freight(self):
        cu_ft = self.cu_ft
        freight_rate_cuft = self.freight_rate_cuft
        qty_master = self.qty_master
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if cu_ft and freight_rate_cuft and qty_master:
            cuft = (cu_ft*freight_rate_cuft)
            freight_unit = ((cuft)/qty_master)
            self.freight_unit = float_repr(float_round(freight_unit, precision_digits=prec),precision_digits=prec)      
    
    @api.onchange('sell_price','duty')
    def onchange_duty(self):
        sell_price = self.sell_price
        duty = self.duty
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if sell_price and duty:
            duty_cost = (sell_price*duty)
            self.duty_cost = float_repr(float_round(duty_cost, precision_digits=prec),precision_digits=prec)      

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
    def _onchange_carton(self):
        group_carton = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_carton')
        group_cu_ft = self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_cu_ft')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if group_carton>0:
            carton_d_in = (float(self.carton_d_cm) * float(group_carton))
            self.carton_d_in = float_repr(float_round(carton_d_in, precision_digits=prec),precision_digits=prec)
            carton_h_in = (float(self.carton_h_cm) * float(group_carton))
            self.carton_h_in = float_repr(float_round(carton_h_in, precision_digits=prec),precision_digits=prec)
            carton_w_in = (float(self.carton_w_cm) * float(group_carton))
            self.carton_w_in = float_repr(float_round(carton_w_in, precision_digits=prec),precision_digits=prec)
            cbm = ((self.carton_d_cm * self.carton_h_cm * self.carton_w_cm)/1000000)
            self.cbm = float_repr(float_round(cbm, precision_digits=prec),precision_digits=prec)
            
        if group_cu_ft > 0:
            cu_ft = (float(self.cbm) * float(group_cu_ft))
            self.cu_ft = float_repr(float_round(cu_ft, precision_digits=prec),precision_digits=prec)
        
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
    
class ProductAttributeColor(models.Model):
    _name = 'product.attr.color'
    _description = "Product Attribute Color"
    _rec_name = 'attribute_id'
    
    attribute_id = fields.Many2one('product.attribute',"Attribute")
    upc = fields.Char("UPC")
    product_id = fields.Many2one('product.template',"Product")
    
    
    @api.multi
    def name_get(self):
        return [(value.id, "%s: %s" % (value.attribute_id.name, value.upc)) for value in self]

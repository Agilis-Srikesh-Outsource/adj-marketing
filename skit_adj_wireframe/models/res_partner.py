# -*- coding: utf-8 -*-

from odoo import fields, models,_


class SkitLineBusiness(models.Model):
    
    _name="skit.line.business"
    
    name = fields.Char(string='Name')

class SkitProductSupplierInfo(models.Model):
    _inherit="product.supplierinfo"
    
    nick_name = fields.Char("Nick Name")
    vendor_item = fields.Char(string="Vendor Item #")
    
class SkiResPartner(models.Model):
    _inherit = 'res.partner'
    _description = "Res Partners"
    
    partner_code = fields.Char(string="Partner Code")
    line_business=fields.Many2one('skit.line.business',string="Line of Business")
    vendor_nickname = fields.Char("Vendor NickName")
    live = fields.Selection([('yes', _('Yes')),
                             ('no',_('No'))], string='Live')
    product_category_id=fields.Many2one('product.category',string="Product Category")
    audit = fields.Selection([('yes', _('Yes')),
                             ('no',_('No'))], string='Audit')
    audit_valid_to = fields.Datetime("Audit Valid To")
    remark = fields.Text(string='Remarks',help="Notes/Remark")
    fax = fields.Char("Fax")
    tax_id = fields.Many2one('account.tax',srting="Tax ID")
    resale = fields.Char("Resale #")
    terms = fields.Char("Terms")
    customer_since = fields.Char("Customer Since")
    
    
    
# -*- coding: utf-8 -*-

from odoo import fields, models,_

class SkitDateConfig(models.Model):
    _name = "skit.date.config"
    _rec_name = 'name'
    
    name = fields.Char("Name",default="")
    start_ship_window = fields.Integer(string="Start of Ship Window")
    po_good_through = fields.Integer(string="PO Good Through",
                                  help="Carols CRD/PO Good Through")
    sa_release_target = fields.Integer(string="SA Release Target")
    so_release_target = fields.Integer(string="SO Release Target")
    qaa_date = fields.Integer("QAA Date")
    inspection_date = fields.Integer("Inspection Date")
    safety_complete = fields.Integer("Safety Completed")
    book_by_date = fields.Integer("Book By Date")
    dupro_date = fields.Integer("Dupro Date")
    sample_collection = fields.Integer("Sample Collection")
    sample_selling = fields.Integer("Sample Selling")
    po_date_receipt = fields.Integer("PO Date Receipt")
    delivery_date = fields.Integer('Delivery Date',
                                copy=False,
                                index=True, readonly=False, store=True,
                                track_visibility='onchange',
                                help="Delivery Date of Transfer")
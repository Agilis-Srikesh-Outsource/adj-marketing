# -*- coding: utf-8 -*-

from odoo import fields, models,_

class SkitShipVia(models.Model):
    _name = "skit.ship.via"
    
    name = fields.Char("Name")
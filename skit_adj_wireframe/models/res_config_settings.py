# -*- coding: utf-8 -*-

from odoo import fields, models,api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    group_carton = fields.Float("Carton")
    group_cu_ft = fields.Float("Cu FT")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            group_carton = float(self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_carton')),
            group_cu_ft = float(self.env['ir.config_parameter'].sudo().get_param('skit_adj_wireframe.group_cu_ft'))
        )
        return res
        
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('skit_adj_wireframe.group_carton', (self.group_carton))
        self.env['ir.config_parameter'].sudo().set_param('skit_adj_wireframe.group_cu_ft', (self.group_cu_ft))

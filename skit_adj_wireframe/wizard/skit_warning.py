from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SkitWarning(models.TransientModel):
    _name = "delivery.warning.wizard"

    name = fields.Char("Name")
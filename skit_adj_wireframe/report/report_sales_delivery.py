# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models


class report_sales_delivery_document(models.AbstractModel):
    _name = 'report.skit_adj_wireframe.report_sales_delivery_document'

    @api.multi
    def get_report_values(self, docids, data=None):
        data = data if data is not None else {}
       
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': data['delivery_detail'],
            'start_date':  data['start_date'],
            'end_date':  data['end_date'],
        }

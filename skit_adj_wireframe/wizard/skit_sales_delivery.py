from odoo import fields, models, api, _
from odoo.exceptions import UserError


class SkitSalesDelivery(models.TransientModel):
    _name = "sale.delivery.wizard"

    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    
    
    @api.multi
    def sales_delivery_action(self):
        params = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            }
        self.env.cr.execute("""
                            select sp.name,
                            sm.product_id,
                            sp.delivery_date,
                            pt.port,
                            pt.name as product_name,
                            rp.name as vendor,
                            ai.adj_po,
                            so.client_order_ref as customerpo,
                            po.name as wbapo,
                            pt.item_no,
                            pt.item_description,
                            ((select sum(product_qty) from purchase_order_line where order_id = po.id ) - (select sum(qty_received) from purchase_order_line where order_id = po.id )) as qtyopen,
                            sp.deadline_book,
                            sp.actual_booked_date,
                            po.crd,
                            sp.received_date,
                            sp.actual_etd,
                            sp.cargo_received_date,
                            po.actual_inspection_date,
                            ai.date_invoice,
                            po.sail_window_start,
                            po.sail_window_end
                            from stock_picking sp
                            inner join stock_move sm on sp.id = sm.picking_id
                            inner join product_product pp on sm.product_id = pp.id
                            inner join product_template pt on pp.product_tmpl_id = pt.id
                            left outer join purchase_request_line prl on sm.id = prl.move_id
                            left outer join purchase_request pr on prl.request_id = pr.id
                            left outer join purchase_order_line pol on prl.purchase_line_id = pol.id
                            left outer join purchase_order po on pol.order_id = po.id
                            left outer join account_invoice_purchase_order_rel aip on po.id =aip.purchase_order_id
                            left outer join account_invoice ai on aip.account_invoice_id = ai.id
                            left outer join sale_order so on sp.sale_id = so.id
                            left outer join res_partner rp on po.partner_id = rp.id
                            where sp.delivery_date BETWEEN %(start_date)s AND %(end_date)s
                            order by sp.name
                    """, params,)
        delivery = self.env.cr.dictfetchall()
        data = {'ids': self.ids,
                'model': self._name,
                'delivery_detail': delivery,
                'start_date': self.start_date,
                'end_date': self.end_date
                }
        return self.env.ref('skit_adj_wireframe.action_report_sale_delivery').report_action(self, data=data)

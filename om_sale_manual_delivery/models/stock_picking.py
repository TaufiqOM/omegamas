
from odoo import SUPERUSER_ID, _, api, Command, fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # group_id = fields.Many2one(
    #     'procurement.group', 'Procurement Group',
    #     readonly=False, related='move_ids.group_id', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Proyek')
    department_id = fields.Many2one('hr.department', string='Department')
    
    def button_validate(self):
        for rec in self:        
            if rec.state == 'assigned' and 'draft' in rec.name.lower():   
                if rec.picking_type_id.sequence_id:
                    rec.name = rec.picking_type_id.sequence_id.next_by_id()
        if any(x.product_uom_qty < x.quantity for x in self.move_ids):
            raise UserError(_('Quantitiy can`t be greater than demand quantity.'))

        return super().button_validate()

    # def write(self, vals):
    #     res = super().write(vals)

    #     if self.state == 'assigned' and 'draft' in self.name.lower():   
    #         if self.picking_type_id.sequence_id:
    #             self.name = self.picking_type_id.sequence_id.next_by_id()
    #     return res    

    @api.model_create_multi
    def create(self, vals_list):
        scheduled_dates = []
        for vals in vals_list:
            defaults = self.default_get(['name', 'picking_type_id'])
            picking_type = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id')))
            if vals.get('name', '/') == 'Draft Backorder':
                vals['name'] = 'Draft Backorder'

            scheduled_dates.append(vals.pop('scheduled_date', False))

        pickings = super().create(vals_list)

        for picking, scheduled_date in zip(pickings, scheduled_dates):
            if scheduled_date:
                picking.with_context(mail_notrack=True).write({'scheduled_date': scheduled_date})
            if picking.name == 'Draft Backorder':
                picking.name = """Draft(*{name})""".format(name=picking.id)
        pickings._autoconfirm_picking()

        for picking, vals in zip(pickings, vals_list):
            # set partner as follower
            if vals.get('partner_id'):
                if picking.location_id.usage == 'supplier' or picking.location_dest_id.usage == 'customer':
                    picking.message_subscribe([vals.get('partner_id')])
            if vals.get('picking_type_id'):
                for move in picking.move_ids:
                    if not move.description_picking:
                        move.description_picking = move.product_id.with_context(lang=move._get_lang())._get_description(move.picking_id.picking_type_id)
        return pickings


    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_backorder._recompute_state()
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': 'Draft Backorder',
                    'move_ids': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id
                })
                moves_to_backorder.write({'picking_id': backorder_picking.id, 'picked': False})
                moves_to_backorder.move_line_ids.package_level_id.write({'picking_id': backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                backorders |= backorder_picking
                picking.message_post(
                    body=_('The backorder %s has been created.', backorder_picking._get_html_link())
                )
                if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                    bo_to_assign |= backorder_picking
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders
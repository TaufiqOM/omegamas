from odoo import models, fields, api
from odoo.exceptions import UserError

class BarcodeProduksiWizardLine(models.TransientModel):
    _name = 'barcode.produksi.wizard.line'
    _description = 'Line Wizard Barcode'

    wizard_id = fields.Many2one('barcode.produksi.wizard', string='Wizard')
    produksi_line_id = fields.Many2one('barcode.produksi.line', string='Line Produksi')
    product_template_id = fields.Many2one(related='produksi_line_id.product_template_id', store=True, readonly=True)
    product_uom_qty = fields.Float(related='produksi_line_id.product_uom_qty', store=True, readonly=True)
    jumlah_generate = fields.Integer(string='Jumlah Generate', default=1)
    belum_generate = fields.Integer(related='produksi_line_id.belum_generate', string='Belum Generate', store=False, readonly=True)

    @api.onchange('jumlah_generate')
    def _onchange_jumlah_generate(self):
        for record in self:
            if record.jumlah_generate > record.produksi_line_id.belum_generate:
                raise UserError("Jumlah Generate Melebihi Stock")

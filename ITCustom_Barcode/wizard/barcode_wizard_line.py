from odoo import models, fields, api

class BarcodeProduksiWizardLine(models.TransientModel):
    _name = 'barcode.produksi.wizard.line'
    _description = 'Line Wizard Barcode'

    wizard_id = fields.Many2one('barcode.produksi.wizard', string='Wizard')
    produksi_line_id = fields.Many2one('barcode.produksi.line', string='Line Produksi')
    product_template_id = fields.Many2one(related='produksi_line_id.product_template_id', store=True, readonly=True)
    product_uom_qty = fields.Float(related='produksi_line_id.product_uom_qty', store=True, readonly=True)
    jumlah_generate = fields.Integer(string='Jumlah Generate', default=1)


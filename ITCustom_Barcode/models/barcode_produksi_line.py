# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Barcode/models/barcode_produksi_line.py
from odoo import models, fields, api


class BarcodeProduksiLine(models.Model):
    _name = 'barcode.produksi.line'
    _description = 'Barcode Produksi Line'

    product_template_id = fields.Many2one('product.template', string='Produk')
    product_uom_qty = fields.Float(string='Quantity', readonly=True)
    produksi_id = fields.Many2one('barcode.produksi', string='Barcode Produksi', ondelete='cascade')
    sudah_generate = fields.Integer(string="Sudah Generate", compute="_compute_generate_counts", store=True)
    belum_generate = fields.Integer(string="Belum Generate", compute="_compute_generate_counts", store=True)

    
    @api.depends('produksi_id.order_id', 'product_template_id', 'product_uom_qty')
    def _compute_generate_counts(self):
        for line in self:
            subkode_model = self.env['barcode.produksi.subkode']
            count = subkode_model.search_count([
                ('order_id', '=', line.produksi_id.order_id.id),
                ('produk_id', '=', line.product_template_id.id),
            ])
            line.sudah_generate = count
            line.belum_generate = line.product_uom_qty - count

# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Barcode/wizard/barcode_wizard.py
from odoo import models, fields, api

class BarcodeProduksiWizard(models.TransientModel):
    _name = 'barcode.produksi.wizard'
    _description = 'Wizard Generate Barcode'

    produksi_id = fields.Many2one('barcode.produksi', string='Barcode Produksi', required=True)
    line_ids = fields.One2many('barcode.produksi.wizard.line', 'wizard_id', string='Daftar Produk')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        produksi = self.env['barcode.produksi'].browse(self.env.context.get('active_id'))
        lines = []
        for line in produksi.product_line_ids:
            lines.append((0, 0, {
                'produksi_line_id': line.id,  # WAJIB DITAMBAHKAN
                'product_template_id': line.product_template_id.id,
                'product_uom_qty': line.product_uom_qty,
                'jumlah_generate': 1,  # default 1
            }))
        res.update({
            'produksi_id': produksi.id,
            'line_ids': lines,
        })
        return res


    def action_generate(self):
        for wizard in self:

            # Ambil kode terakhir dari database, atau mulai dari 200000
            last_kode = self.env['barcode.produksi.subkode'].search([], order='kode desc', limit=1).kode
            try:
                start_kode = int(last_kode) + 1 if last_kode else 200000
            except (ValueError, TypeError):
                start_kode = 200000

            for line in wizard.line_ids:
                jumlah_generate = line.jumlah_generate
                for i in range(jumlah_generate):
                    seq = f"{i + 1:04d}"
                    jumlah = f"{jumlah_generate:04d}"
                    sub_kode = f"{start_kode}-{seq}-{jumlah}"

                    self.env['barcode.produksi.subkode'].create({
                        'name': sub_kode,
                        'kode': str(start_kode),
                        'produk_id': line.product_template_id.id,
                        'produksi_id': wizard.produksi_id.id,
                        'order_id': wizard.produksi_id.order_id.id,
                    })

                start_kode += 1  # Naikkan untuk produk berikutnya


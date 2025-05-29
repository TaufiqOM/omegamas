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
                'produksi_line_id': line.id,
                'product_template_id': line.product_template_id.id,
                'product_uom_qty': line.product_uom_qty,
                'jumlah_generate': 1,
            }))
        res.update({
            'produksi_id': produksi.id,
            'line_ids': lines,
        })
        return res

    def action_generate(self):
        for wizard in self:
            # Tidak mengambil sequence di awal, melainkan di dalam loop line_ids
            for line in wizard.line_ids:
                # Ambil sequence baru untuk setiap produk
                sequence = self.env['ir.sequence'].next_by_code('barcode.produksi.subkode')
                if not sequence:
                    # Jika sequence belum ada, buat sequence baru dengan kode awal 200000
                    sequence_obj = self.env['ir.sequence'].create({
                        'name': 'Barcode Produksi Subkode',
                        'code': 'barcode.produksi.subkode',
                        'prefix': '',
                        'padding': 6,
                        'number_increment': 1,
                        'number_next_actual': 200000,
                    })
                    sequence = sequence_obj.next_by_code('barcode.produksi.subkode')

                start_kode = int(sequence)  # Inisialisasi start_kode untuk produk ini

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
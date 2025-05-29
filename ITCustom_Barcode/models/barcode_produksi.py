# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Barcode/models/barcode_produksi.py
import base64
from io import BytesIO
import qrcode
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BarcodeProduksi(models.Model):
    _name = 'barcode.produksi'
    _description = 'barcode produksi'
    _order = 'id desc'

    order_id = fields.Many2one(
        'sale.order',
        string='Nomor Penjualan',
        domain=lambda self: [('state', '=', 'sale'), ('id', 'not in', self._get_used_order_ids())],
        required=True
    )

    def _get_used_order_ids(self):
        used_order_ids = self.search([]).mapped('order_id').ids
        return used_order_ids
    product_line_ids = fields.One2many(
        'barcode.produksi.line', 
        'produksi_id', 
        string='Daftar Produk',
        compute='_compute_product_lines',
        store=True  # Opsional, tergantung kebutuhan
    )
    
    barcode_image = fields.Binary("Barcode", store=True)
    subkode_ids = fields.One2many('barcode.produksi.subkode', 'produksi_id', string="Sub Kode")
    
    @api.constrains('order_id')
    def _check_unique_order_id(self):
        for record in self:
            if record.order_id:
                existing = self.search([('order_id', '=', record.order_id.id), ('id', '!=', record.id)])
                if existing:
                    raise ValidationError("Barcode dengan Kode SO yang sama sudah dibuat.")
    
    def open_generate_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Barcode',
            'res_model': 'barcode.produksi.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_produksi_id': self.id,
            }
        }

    def _generate_barcode(self):
        for record in self:
            if record.order_id:
                data = record.order_id.name
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill='black', back_color='white')
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                record.barcode_image = base64.b64encode(buffer.getvalue())

                
    @api.onchange('order_id')
    def _onchange_order_id(self):
        for record in self:
            # Pastikan untuk menghapus semua line yang ada terlebih dahulu
            record.product_line_ids = [(5, 0, 0)]
            
            if record.order_id:
                # Buat list baru hanya dengan produk yang valid
                valid_lines = []
                for line in record.order_id.order_line:
                    if line.product_id and line.product_id.product_tmpl_id:
                        valid_lines.append((0, 0, {
                            'product_template_id': line.product_id.product_tmpl_id.id,
                            'product_uom_qty': line.product_uom_qty
                        }))
                
                # Update dengan line yang valid saja
                if valid_lines:
                    record.product_line_ids = valid_lines
                else:
                    record.product_line_ids = [(5, 0, 0)]  # Kosongkan jika tidak ada produk valid
                    
    @api.depends('order_id.order_line.product_id.product_tmpl_id')
    def _compute_product_lines(self):
        for record in self:
            record.product_line_ids = [(5, 0, 0)]  # Clear existing lines
            if record.order_id:
                record.product_line_ids = [(0, 0, {
                    'product_template_id': line.product_id.product_tmpl_id.id,
                    'product_uom_qty': line.product_uom_qty  # Tambahkan quantity
                }) for line in record.order_id.order_line 
                if line.product_id and line.product_id.product_tmpl_id]

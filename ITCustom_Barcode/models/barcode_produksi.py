# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Barcode/models/barcode_produksi.py
import base64
from io import BytesIO
import qrcode
from odoo import models, fields, api

class BarcodeProduksi(models.Model):
    _name = 'barcode.produksi'
    _description = 'barcode produksi'

    order_id = fields.Many2one(
        'sale.order',
        string='Nomor Penjualan',
        domain="[('state', '=', 'sale')]",
        required=True
    )
    
    barcode_image = fields.Binary("Barcode", compute="_generate_barcode", store=True)

    @api.depends('order_id')
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


# models/barcode_subkode.py
from odoo import models, fields

class BarcodeProduksiSubkode(models.Model):
    _name = 'barcode.produksi.subkode'
    _description = 'Sub Kode Barcode Produksi'

    name = fields.Char("Kode Barcode", required=True)
    order_id = fields.Many2one('sale.order', string='Nomor Penjualan')
    produk_id = fields.Many2one('product.template', string="Produk", required=True)
    produksi_id = fields.Many2one('barcode.produksi', string="Barcode Produksi", ondelete='cascade')
    kode = fields.Char(string="Kode", required=True)
    

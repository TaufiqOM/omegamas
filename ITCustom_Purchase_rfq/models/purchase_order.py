from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    name = fields.Char(string="Order Reference", readonly=True, copy=False, unique=True)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == '/':
            vals['name'] = self._generate_draft_name()
        return super(PurchaseOrder, self).create(vals)

    def _generate_draft_name(self):
        """ Generate nama Draft unik jika sudah ada "Draft - 1", maka menjadi "Draft - 2", dst. """
        existing_drafts = self.search([('name', '=like', 'Draft - %')], order='name desc', limit=1)
        if existing_drafts:
            last_number = existing_drafts.name.replace('Draft - ', '').strip()
            new_number = int(last_number) + 1 if last_number.isdigit() else 1
            return f"Draft - {new_number}"
        return "Draft - 1"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.date_order:
                order.date_approve = order.date_order  # Gunakan date_order untuk date_approve
            
            # Update nomor PO saat konfirmasi
            order._update_po_number()
        
        return res

    def write(self, vals):
        """ Jika date_order berubah setelah status kembali ke draft, update nomor PO """
        res = super(PurchaseOrder, self).write(vals)
        if 'date_order' in vals and self.state == 'draft':
            self._update_po_number()
        return res

    def _update_po_number(self):
        """ Generate nomor PO berdasarkan Tahun/Bulan dengan timezone WIB (UTC+7) """
        for order in self:
            if order.state == 'draft' and order.date_order:
                # Konversi date_order ke timezone WIB
                date_wib = order.date_order + timedelta(hours=7)

                year = date_wib.strftime('%y')
                month = date_wib.strftime('%m')

                # Cari jumlah PO di bulan & tahun yang sama dengan timezone WIB
                last_po = self.search([
                    ('name', 'like', f'PO {year}/{month}/%'),
                    ('id', '!=', order.id)  # Hindari konflik dengan PO sendiri
                ], order='name desc', limit=1)

                if last_po:
                    last_number = int(last_po.name.split('/')[-1]) + 1
                else:
                    last_number = 1  # Reset ke 1 jika bulan baru

                new_name = f"PO {year}/{month}/{last_number:03d}"
                order.name = new_name  # Set nama baru

    @api.constrains('name')
    def _check_unique_name(self):
        for order in self:
            if self.search_count([('name', '=', order.name)]) > 1:
                raise ValidationError(f"Nomor PO '{order.name}' sudah ada! Harap gunakan nomor yang unik.")

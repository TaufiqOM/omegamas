# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestAccountAccount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.AccountAccount = cls.env["account.account"]
        cls.account_type_current_liabilities = "liability_current"
        cls.account_type_liquidity = "asset_cash"
        cls.company = cls.env.ref("om_account_multicurrency_revaluation.res_company_reval")
        cls.env.user.write({"company_ids": [(4, cls.company.id, False)]})
        cls.env.company = cls.company

    def test_currency_revaluation_field(self):
        with common.Form(self.AccountAccount, view="account.view_account_form") as form:
            form.name = "Test Account"
            form.code = "TEST"
            form.account_type = self.account_type_current_liabilities
            account = form.save()

        self.assertFalse(account.currency_revaluation)

        with common.Form(account, view="account.view_account_form") as form:
            form.account_type = self.account_type_liquidity
            account = form.save()

        self.assertTrue(account.currency_revaluation)

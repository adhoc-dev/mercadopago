from odoo import models, fields, api


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    token_card = fields.Char(
        string="Token card",
        readonly=True)
    card_id = fields.Char(
        string="Card",
        readonly=True)
    installments = fields.Integer()
    acquirer_ref = fields.Char('Acquirer Ref.', required=False)
    issuer_id = fields.Integer()
    mercadopago = fields.Boolean()
    payment_method_id = fields.Char()

    # cvv = fields.Char()

    def get_name_to_token_payment(self, card_name, partner_name):
        name_token = card_name + ' - ' + partner_name
        return name_token

    @api.model
    def mercadopago_create_payment_token(
            self,
            card_name,
            partner_id,
            issuer_id,
            installments,
            payment_method_id,
            token_card,
            payment_id,
            card_id=''
    ):
        tokens = self.sudo().search([('partner_id', '=', partner_id)],
                                    order='create_date')
        if len(tokens) >= 3:
            tokens[0].unlink()
        partner = self.env['res.partner'].sudo().browse(partner_id)
        token_name = self.get_name_to_token_payment(card_name, partner.name)
        try:
            payment_token = self.sudo().create(
                {
                    'name': token_name,
                    'partner_id': partner_id,
                    'acquirer_id': payment_id.id,
                    'token_card': token_card,
                    'verified': True,
                    'payment_method_id': payment_method_id,
                    'installments': installments,
                    'issuer_id': issuer_id,
                    'mercadopago': True,
                    'card_id': card_id
                }
            )
        except Exception as e:
            payment_token = False
        return payment_token

# coding: utf-8

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentAcquirerMercadoPago(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('mercadopago', 'MercadoPago')])
    mercadopago_client_id = fields.Char(
        'MercadoPago Client Id',
        required_if_provider='mercadopago')
    mercadopago_secret_key = fields.Char(
        'MercadoPago Secret Key',
        required_if_provider='mercadopago')
    mercadopago_publishable_key = fields.Char(
        'MercadoPago Publishable Key',
        required_if_provider='mercadopago')
    mercadopago_url = fields.Char(
        'MercadoPago url',
        required_if_provider='mercadopago')
    mercadopago_authorize_amount = fields.Float(
        string='Authorize amount'
    )

    @api.constrains('mercadopago_authorize_amount', 'state')
    def _validate_mercadopago_authorize_amount(self):
        if self.state != 'disabled' and self.mercadopago_authorize_amount <= 0:
            raise ValidationError(_(
                "El monto de autorizo debe ser positivo, equivalente a 1 USD en "
                "moneda local."))


    @api.onchange('provider', 'check_validity')
    def onchange_check_validity(self):
        if self.provider == 'mercadopago' and self.check_validity:
            self.check_validity = False
            return {'warning': {
                'title': _("Warning"),
                'message': ('This option is not supported for MercadoPago')}}

    # def action_client_secret(self):
    #     return True

    # def _get_feature_support(self):
    #     """Get advanced feature support by provider.
    #
    #     Each provider should add its technical in the corresponding
    #     key for the following features:
    #         * fees: support payment fees computations
    #         * authorize: support authorizing payment (separates
    #                      authorization and capture)
    #         * tokenize: support saving payment data in a payment.tokenize
    #                     object
    #     """
    #     res = super(PaymentAcquirerMercadoPago, self)._get_feature_support()
    #     res['authorize'].append('mercadopago')
    #     res['tokenize'].append('mercadopago')
    #     return res

    # def _get_mercadopago_urls(self, environment):
    #     """ MercadoPago URLs """
    #     if environment == 'prod':
    #         return {'mercadopago_form_url': 'https://www.mercadopago.com.ar/'}
    #     else:
    #         return {'mercadopago_form_url': 'https://www.mercadopago.com.ar/'}

    # def mercadopago_form_generate_values(self, values):
    #     self.ensure_one()
    #     mercadopago_tx_values = dict(values)
    #     base_url = self.get_base_url()
    #     temp_mercadopago_tx_values = {
    #         'x_amount': float_repr(values['amount'],
    #                                values['currency'].decimal_places
    #                                if values['currency'] else 2),
    #         'x_show_form': 'PAYMENT_FORM',
    #         'x_type': 'AUTH_CAPTURE' if not self.capture_manually
    #         else 'AUTH_ONLY',
    #         'x_method': 'CC',
    #         'x_fp_sequence': '%s%s' % (self.id, int(time.time())),
    #         'x_version': '3.1',
    #         'x_relay_response': 'TRUE',
    #         'x_fp_timestamp': str(int(time.time())),
    #         'x_relay_url': urls.url_join(base_url,
    #                                      MercadoPagoController._success_url),
    #         'x_cancel_url': urls.url_join(base_url,
    #                                       MercadoPagoController._failure_url),
    #         'x_currency_code': values['currency'] and values['currency'].name
    #                            or '',
    #         'address': values.get('partner_address'),
    #         'city': values.get('partner_city'),
    #         'country': values.get('partner_country')
    #                    and values.get('partner_country').name or '',
    #         'email': values.get('partner_email'),
    #         'zip_code': values.get('partner_zip'),
    #         'first_name': values.get('partner_first_name'),
    #         'last_name': values.get('partner_last_name'),
    #         'phone': values.get('partner_phone'),
    #         'billing_address': values.get('billing_partner_address'),
    #         'billing_city': values.get('billing_partner_city'),
    #         'billing_country': values.get('billing_partner_country')
    #                            and values.get('billing_partner_country').name
    #                            or '',
    #         'billing_email': values.get('billing_partner_email'),
    #         'billing_zip_code': values.get('billing_partner_zip'),
    #         'billing_first_name': values.get('billing_partner_first_name'),
    #         'billing_last_name': values.get('billing_partner_last_name'),
    #         'billing_phone': values.get('billing_partner_phone'),
    #     }
    #     mercadopago_tx_values.update(temp_mercadopago_tx_values)
    #     return mercadopago_tx_values

    # def mercadopago_get_form_action_url(self):
    #     self.ensure_one()
    #     environment = 'prod' if self.state == 'enabled' else 'test'
    #     return self._get_mercadopago_urls(environment)['mercadopago_form_url']

    # @api.model
    # def mercadopago_s2s_form_process(self, data):
    #     return False
    #
    # def mercadopago_s2s_form_validate(self, data):
    #     error = dict()
    #     return False if error else True


# class PaymentTransactionMercadoPago(models.Model):
#     _inherit = 'payment.transaction'
#
#     # TODO: This fields probably will be deleted
#     mercadopago_txn_id = fields.Char(
#         'Transaction ID')
#     mercadopago_txn_type = fields.Char(
#         'Transaction type',
#         help='Informative field computed after payment')
#
#     # --------------------------------------------------
#     # FORM RELATED METHODS
#     # --------------------------------------------------
#
#     @api.model
#     def _mercadopago_form_get_tx_from_data(self, data):
#         """ Given a data dict coming from mercadopago, verify it and find the
#         related transaction record. """
#         pass
#
#     def _mercadopago_form_get_invalid_parameters(self, data):
#         invalid_parameters = []
#         return invalid_parameters
#
#     def _mercadopago_form_validate(self, data):
#         return False
#
#     # --------------------------------------------------
#     # SERVER2SERVER RELATED METHODS
#     # --------------------------------------------------
#
#     def mercadopago_s2s_do_transaction(self, **data):
#         self.ensure_one()
#         return False
#
#     def mercadopago_s2s_do_refound(self, **data):
#         self.ensure_one()
#         return False
#
#     def mercadopago_s2s_capture_transaction(self):
#         self.ensure_one()
#         return False
#
#     def mercadopago_s2s_void_transaction(self):
#         self.ensure_one()
#         return False
#
#     def mercadopago_s2s_get_tx_status(self):
#         self.ensure_one()
#         return False


class ResPartner(models.Model):
    _inherit = 'res.partner'
    lastname = fields.Char()
    mp_id = fields.Char()


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    mercadopago_profile = fields.Char(
        string='MercadoPago Profile ID',
        help='This contains the unique reference for this partner/payment '
             'token combination in the mercadopago backend')
    provider = fields.Selection(
        string='Provider',
        related='acquirer_id.provider',
        readonly=False)
    save_token = fields.Selection(
        string='Save Cards',
        related='acquirer_id.save_token',
        readonly=False)

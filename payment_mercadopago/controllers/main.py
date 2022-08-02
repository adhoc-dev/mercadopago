##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import logging
import pprint
import werkzeug
from odoo import http
from odoo.http import request, Response
from odoo.tools.safe_eval import safe_eval
from odoo.addons.payment_mercadopago.models.mercadopago_request import MercadoPagoAPI
from urllib import parse
import json
_logger = logging.getLogger(__name__)


class MercadoPagoController(http.Controller):

    @http.route(['/payment/mercadopago/create_preference'], type='http', auth="none", csrf=False)
    def mercadopago_create_preference(self, **post):
        # TODO podriamos pasar cada elemento por separado para no necesitar
        # el literal eval
        acquirer = request.env['payment.acquirer'].browse(safe_eval(post.get('acquirer_id'))).sudo()
        preference = safe_eval(post.get('mercadopago_preference'))

        if not acquirer:
            return werkzeug.utils.redirect("/")

        MP = MercadoPagoAPI(acquirer)
        linkpay = MP.create_preference(preference)
        return werkzeug.utils.redirect(linkpay)

    @http.route([
        '/payment/mercadopago/success',
        '/payment/mercadopago/pending',
        '/payment/mercadopago/failure'
    ], type='http', auth="none")
    def mercadopago_back_no_return(self, **post):
        """
        Odoo, si usas el boton de pago desde una sale order o email, no manda
        una return url, desde website si y la almacena en un valor que vuelve
        desde el agente de pago. Como no podemos mandar esta "return_url" para
        que vuelva, directamente usamos dos distintas y vovemos con una u otra
        """
        _logger.info('Mercadopago: entering mecadopago_back with post data %s', pprint.pformat(post))
        request.env['payment.transaction'].sudo().form_feedback(post, 'mercadopago')
        return werkzeug.utils.redirect("/payment/process")

    @http.route(['/payment/mercadopago/s2s/create_json_3ds'], type='json', auth='public', csrf=False)
    def mercadopago_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        if not kwargs.get('partner_id'):
            kwargs = dict(kwargs, partner_id=request.env.user.partner_id.id)
        token = False
        error = None

        try:
            token = request.env['payment.acquirer'].browse(int(kwargs.get('acquirer_id'))).s2s_process(kwargs)
        except Exception as e:
            error = str(e)

        if not token:
            res = {
                'result': False,
                'error': error,
            }
            return res

        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
            '3d_secure': False,
            'verified': False,
        }
        if verify_validity:
            token.validate()
            res['verified'] = token.verified

        return res

    @http.route(['/payment/mercadopago/s2s/otp'], type='json', auth='public')
    def mercadopago_s2s_otp(self, **kwargs):
        cvv_token = kwargs.get('token')
        # request.session.update(kwargs)
        request.session.update({'cvv_token': cvv_token})
        return {'result': True}

    @http.route(['/payment/mercadopago/notification',
                 '/payment/mercadopago/notification/<int:acquirer_id>'],
                type='json', methods=['POST'], auth='public')
    def mercadopago_s2s_notification(self, acquirer_id=False, **kwargs):
        querys = parse.urlsplit(request.httprequest.url).query
        params = dict(parse.parse_qsl(querys))
        if (params and params.get('payment_type') == 'payment' and params.get('data.id')):
            leaf = [('provider', '=', 'mercadopago')]
            if acquirer_id:
                leaf += [('id', '=', acquirer_id)]
            acquirer = request.env["payment.acquirer"].search(leaf)
            payment_id = params['data.id']
            tx = request.env['payment.transaction'].sudo().search(
                [('acquirer_reference', '=', payment_id)])
            MP = MercadoPagoAPI(acquirer)
            tree = MP.get_payment(payment_id)
            return tx._mercadopago_s2s_validate_tree(tree)
        return False

    @http.route(['/payment/mercadopago/notify',
                 '/payment/mercadopago/notify/<int:acquirer_id>'],
                type='json', auth='none')
    def mercadopago_notification(self,acquirer_id=False):
        """ Process the data sent by MercadoPago to the webhook based on the event code.
        :return: Status 200 to acknowledge the notification
        :rtype: Response
        """
        data = json.loads(request.httprequest.data)
        _logger.debug("MercadoPago notification: \n%s", pprint.pformat(data))
        if data['type'] == 'payment':
            try:
                # Payment ID
                payment_id = data['data']['id']

                # Get payment data from MercadoPago
                leaf = [('provider', '=', 'mercadopago')]
                if acquirer_id:
                    leaf += [('id', '=', acquirer_id)]

                acquirer = request.env["payment.acquirer"].sudo().search(leaf, limit=1)
                MP = MercadoPagoAPI(acquirer)
                tree = MP.get_payment(payment_id)
                tx = request.env['payment.transaction'].sudo().search(
                    [('acquirer_reference', '=', payment_id), 
                     ('acquirer_id', '=', acquirer.id)]
                )
                tx._mercadopago_s2s_validate_tree(tree)

            except Exception:  # Acknowledge the notification to avoid getting spammed
                _logger.exception(
                    "Unable to handle the notification data; skipping to acknowledge")

        # Acknowledge the notification
        return Response('success', status=200)

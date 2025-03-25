


class PaymentMethod:

    @classmethod
    def create_payment_method_and_line(cls, request, payment_method_data, payment_type):
        method = request.env['account.payment.method'].sudo().create({
            'name': f"{payment_method_data['name']} ({payment_type.capitalize()})",
            'code': f"{payment_method_data['code']}_{payment_type[:2]}",
            'payment_type': payment_type
        })
        
        line = request.env['account.payment.method.line'].sudo().create({
            'name': method.name,
            'payment_method_id': method.id,
            'journal_id': payment_method_data['journal_id'],
            'payment_account_id': payment_method_data['payment_account_id']
        })
        
        return method, line
    
    @classmethod
    def create_payment_method(cls, request, name, code, journal_id, account_id):
        payment_method_data = {
            'name': name,
            'code': code,
            'journal_id': journal_id,
            'payment_account_id': account_id
        }
        # Create inbound and outbound payment methods and their lines
        inbound_method, inbound_line = cls.create_payment_method_and_line(request, payment_method_data, 'inbound')
        outbound_method, outbound_line = cls.create_payment_method_and_line(request, payment_method_data, 'outbound')




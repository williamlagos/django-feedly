from django.forms import Form,CharField

class BasketForm(Form):
    business = CharField(max_length=100)
    notify_url = CharField(max_length=100)
    return_url = CharField(max_length=100)
    cancel_return = CharField(max_length=100)
    currency_code = CharField(max_length=10)
    def render(self): return ''
    def form(self): return ''

try:
	from cartridge.shop.forms import OrderForm
except ImportError,e:
	class OrderForm(Form):
		pass

class ExternalPaymentOrderForm(OrderForm):
	def __init__(self,*args,**kwargs):
		super(ExternalPaymentOrderForm,self).__init__(*args,**kwargs)
		del self.fields['card_expiry_year']

for field in ('card_name', 'card_type', 'card_number', 'card_expiry_month', 'card_ccv'):
	del ExternalPaymentOrderForm.base_fields[field]
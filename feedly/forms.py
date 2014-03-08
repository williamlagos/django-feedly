from django.forms import Form,CharField,ChoiceField,RadioSelect

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
	GATEWAYS = (
       (1, "PayPal"),
       (2, "PagSeguro"), 
   	)
   	pay_option = ChoiceField(widget=RadioSelect,choices=GATEWAYS)
	def __init__(self,*args,**kwargs):
		super(ExternalPaymentOrderForm,self).__init__(*args,**kwargs)
		del self.fields['card_expiry_year']

excluded = ('card_name','card_type','card_number','card_expiry_month','card_ccv',
			'billing_detail_street','billing_detail_city','billing_detail_state',
			'billing_detail_country','shipping_detail_street','shipping_detail_city',
			'shipping_detail_state','shipping_detail_country')

for field in excluded:
	del ExternalPaymentOrderForm.base_fields[field]
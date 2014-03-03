from django.forms import Form,CharField

class BasketForm(Form):
    business = CharField(max_length=100)
    notify_url = CharField(max_length=100)
    return_url = CharField(max_length=100)
    cancel_return = CharField(max_length=100)
    currency_code = CharField(max_length=10)
    def render(self): return ''
    def form(self): return ''

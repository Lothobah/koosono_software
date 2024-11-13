from django import forms
from .models import Product, Sale

class ProductForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'})
    )
    cost_price = forms.DecimalField(
        max_digits=30,
        decimal_places=2, required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cost price'})
    )
    selling_price = forms.DecimalField(
        max_digits=30,
        decimal_places=2, required= True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter selling price'})
    )
    quantity_in_stock = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity in stock'})
    )
    #image = forms.ImageField(
        #required=False,
        #widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    #)

    class Meta:
        model = Product
        fields = ['name', 'cost_price', 'selling_price', 'quantity_in_stock']

    def clean(self):
        cleaned_data = super().clean()
        cost_price = cleaned_data.get("cost_price")
        selling_price = cleaned_data.get("selling_price")

        if cost_price and selling_price and cost_price > selling_price:
            self.add_error("selling_price", "Selling price should be greater than or equal to cost price.")
        return cleaned_data
class SaleForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, label="Quantity",
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity to be sold'}))

    class Meta:
        model = Sale
        fields = ['quantity']
        
class PinForm(forms.Form):
    pin = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 150px;'}), max_length=4, label="Enter PIN")
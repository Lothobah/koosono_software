from django.shortcuts import render
from django.db.models.fields import files
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
import datetime
from django.db.models import Sum
from django.contrib import admin, messages
from django.urls.conf import path
from django.contrib.auth.models import auth
from koosono_agro_app.forms import ProductForm, SaleForm, PinForm
from django.core.files.storage import FileSystemStorage
from koosono_agro_app.models import Product, Sale, Purchase
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from .models import Product
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Count
from django.conf import settings
from .decorators import require_pin_authentication

CORRECT_PIN = settings.CORRECT_PIN

def pin_authentication_view(request):
    next_url = request.GET.get('next', 'product_list')  # Default to 'product_list' if 'next' not provided
    
    if request.method == "POST":
        form = PinForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            if pin == CORRECT_PIN:
                # Set session flag temporarily
                request.session['pin_authenticated'] = True
                # Redirect to the original page requested
                return redirect(request.session.get('next', next_url))
            else:
                messages.error(request, "Incorrect PIN. Please try again.")
    else:
        form = PinForm()
        # Store the next URL to redirect to after successful PIN entry
        request.session['next'] = next_url
    
    return render(request, 'admin_templates/pin_authentication.html', {'form': form})


@csrf_exempt
def homepage(request):
    if request.method == "POST":
        try:
            # Parse the received data
            data = json.loads(request.body)
            total_sales = 0

            # Iterate through the received products and process the sale for each product
            for item in data.get('products', []):
                product_id = item.get('product_id')  # Get the product_id
                quantity = item.get('quantity')
                total_cost = item.get('total_cost')  # Get the total_cost
                product = Product.objects.get(id=product_id)
                
                # Ensure there is enough stock
                if quantity > product.quantity_in_stock:
                    return JsonResponse({"success": False, "error": f"Not enough stock for {product.name}"}, status=400)
                
                # Create a sale and update the stock
                sale = Sale(product=product, quantity=quantity, total_amount=total_cost)
                sale.save()
                
                # Reduce the stock in the product model
                product.quantity_in_stock -= quantity
                product.save()

                # Update the total sales amount
                total_sales += total_cost
            # Return a JSON response with the success message
            success_message = 'Sales data submitted successfully! Total Amount: GHS {:.2f}'.format(total_sales)
            # Return a successful response
            return JsonResponse({"success": True, "message": success_message, "total_sales": total_sales})

        except Exception as e:
            # If something goes wrong, return the error message
            return JsonResponse({"success": False, "error": str(e)})

    # GET request: Display products on the homepage
    products = Product.objects.all().order_by("name")
    return render(request, "admin_templates/homepage.html", {"products": products})

def search_product(request):
    query = request.GET.get('query', '')
    if query:
        products = Product.objects.filter(name__icontains=query).values('id', 'name', 'selling_price', 'quantity_in_stock')
        return JsonResponse(list(products), safe=False)
    return JsonResponse([], safe=False)

def add_product(request):
    form = ProductForm()
    return render(request, "admin_templates/add_product.html", {"form": form})
def add_product_save(request):
    
    if request.method != "POST":
        return HttpResponse("Method not allowed")
    else:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            cost_price = form.cleaned_data["cost_price"]
            selling_price = form.cleaned_data["selling_price"]
            quantity_in_stock = form.cleaned_data["quantity_in_stock"]
            #image = request.FILES['image']
            #fs = FileSystemStorage()
            #filename = fs.save(image.name, image)
            #image_url = fs.url(filename)
            product = Product(name=name, cost_price=cost_price, selling_price=selling_price, quantity_in_stock=quantity_in_stock)

            product.save()

                # Fetch fees for the student's level and assign to the student
                # Ensure you only retrieve one entry per level
            
            messages.success(request, f"{product.name} has been successfully saved.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            #except Exception as e:

                #messages.error(request, "We encountered an issue. Please try again, or contact support if the problem persists.")
                #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, "We encountered an issue. Please try again, or contact support if the problem persists.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def enter_sale(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > product.quantity_in_stock:
                messages.error(request, "Not enough stock available to complete the sale.")
            else:
                # Calculate total sale amount
                total_amount = product.selling_price * quantity

                # Create the sale and update stock
                sale = Sale(product=product, quantity=quantity, total_amount=total_amount)
                sale.save()
                
                # Update product stock
                product.quantity_in_stock -= quantity
                product.save()

                messages.success(request, "Sale completed successfully!")
                return redirect('homepage')  # Redirect to the product list page
    else:
        form = SaleForm()

    return render(request, 'admin_templates/enter_sale.html', {'form': form, 'product': product})

def sales_report(request):
    
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)

    # Calculate sales for each period
    sales_today = Sale.objects.filter(sale_date__date=today)
    sales_this_week = Sale.objects.filter(sale_date__date__gte=start_of_week)
    sales_this_month = Sale.objects.filter(sale_date__date__gte=start_of_month)
    sales_this_year = Sale.objects.filter(sale_date__date__gte=start_of_year)

    # Aggregating total sales amount, profit, and quantity for each period
    def get_totals(queryset):
        total_sales = queryset.aggregate(total_sales=Sum(F('quantity') * F('product__selling_price')))['total_sales'] or 0
        total_profit = queryset.aggregate(
            total_profit=Sum(ExpressionWrapper(F('quantity') * (F('product__selling_price') - F('product__cost_price')), output_field=DecimalField()))
        )['total_profit'] or 0
        total_quantity = queryset.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        return total_sales, total_profit, total_quantity

    daily_totals = get_totals(sales_today)
    weekly_totals = get_totals(sales_this_week)
    monthly_totals = get_totals(sales_this_month)
    yearly_totals = get_totals(sales_this_year)

    # Yearly historical data
    yearly_data = (
        Sale.objects.annotate(year=F('sale_date__year'))
        .values('year')
        .annotate(
            total_sales=Sum(F('quantity') * F('product__selling_price')),
            total_profit=Sum(ExpressionWrapper(F('quantity') * (F('product__selling_price') - F('product__cost_price')), output_field=DecimalField())),
            total_quantity=Sum('quantity')
        )
        .order_by('-year')
    )

    # Aggregating product quantities for each period
    def get_product_quantities(queryset):
        return queryset.values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('product__selling_price'))
        )

    daily_product_quantities = get_product_quantities(sales_today)
    weekly_product_quantities = get_product_quantities(sales_this_week)
    monthly_product_quantities = get_product_quantities(sales_this_month)
    yearly_product_quantities = get_product_quantities(sales_this_year)

    context = {
        'start_of_week': start_of_week,
        'start_of_month': start_of_month,
        'start_of_year': start_of_year,
        'today': today,
        'sales_today': sales_today,
        'daily_totals': daily_totals,
        'daily_product_quantities': daily_product_quantities,
        'sales_this_week': sales_this_week,
        'weekly_totals': weekly_totals,
        'weekly_product_quantities': weekly_product_quantities,
        'sales_this_month': sales_this_month,
        'monthly_totals': monthly_totals,
        'monthly_product_quantities': monthly_product_quantities,
        'sales_this_year': sales_this_year,
        'yearly_totals': yearly_totals,
        'yearly_product_quantities': yearly_product_quantities,
        'yearly_data': yearly_data,
    }

    return render(request, 'admin_templates/sales_report.html', context)

def product_list(request):
    
    products = Product.objects.all()
    products = Product.objects.annotate(
    total_cost_price=F('cost_price') * F('quantity_in_stock'),
    latest_purchase_date=Max('purchases__purchase_date')
)
    overall_total_cost_price = products.aggregate(total=Sum(F('cost_price') * F('quantity_in_stock')))['total']
    
    return render(request, 'admin_templates/product_list.html', {'products': products, 'overall_total_cost_price': overall_total_cost_price})

def add_purchase(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 0))
        total_cost = product.cost_price * quantity

        # Create new Purchase entry
        purchase = Purchase.objects.create(product=product, quantity=quantity, total_cost=total_cost, purchase_date=timezone.now())
        
        # Update product quantity
        product.quantity_in_stock = F('quantity_in_stock') + quantity
        product.save()

        # Send updated data back to the page
        product.refresh_from_db()
        product_total_cost_price = product.cost_price * product.quantity_in_stock
        overall_total_cost_price = Product.objects.aggregate(total=Sum(F('cost_price') * F('quantity_in_stock')))['total']
        
        return JsonResponse({
            'product_id': product.id,
            'new_quantity': product.quantity_in_stock,
            'product_total_cost_price': product_total_cost_price,
            'overall_total_cost_price': overall_total_cost_price,
            'purchase_date': format(purchase.purchase_date, 'D. F j, Y')  # Format as 'Month day, Year'
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)

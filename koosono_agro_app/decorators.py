# decorators.py
from django.shortcuts import redirect

def require_pin_authentication(view_func):
    def wrapper(request, *args, **kwargs):
        # Redirect to PIN page if the session key is not set
        if not request.session.get('pin_authenticated'):
            return redirect('pin_authentication')
        
        # If authenticated, proceed with the view
        response = view_func(request, *args, **kwargs)
        
        # Remove the session flag after the view is accessed
        if 'pin_authenticated' in request.session:
            del request.session['pin_authenticated']
        
        return response
    return wrapper

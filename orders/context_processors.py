from .cart_utils import get_cart_summary

def cart_context(request):
    cart_summary = get_cart_summary(request)
    return {
        'cart_total_quantity': cart_summary['total_quantity'],
        'cart_total_price': cart_summary['total_price']
    }
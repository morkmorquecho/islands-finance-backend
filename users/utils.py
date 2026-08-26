from django.core.validators import RegexValidator

from core.utils.upload_images import generate_upload_path


phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

def upload_address(instance, filename):
    return generate_upload_path('address', instance, filename, purpose='prueba', owner_field='user')
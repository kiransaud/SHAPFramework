from django.core import signing

def generate_email_confirmation_token(user):
    data = {'user_id': user.pk}
    return signing.dumps(data, salt='email_confirmation')


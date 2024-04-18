from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import EmailMessage



def sendWelcomeEmail(to_email):
    from_email = settings.EMAIL_HOST_USER
    subject = 'Welcome mail'
    email = 'Welcome mail'
    html_c = get_template('common/welcome_mail.html')
    d = { 'email': email }
    html_content = html_c.render(d)
    msg = EmailMultiAlternatives(subject, email, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=settings.EMAIL_HOST_USER,
      to=[data['to_email']]
    )
    email.send()
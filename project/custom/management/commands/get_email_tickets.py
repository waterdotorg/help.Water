import email
import imaplib
import quopri


from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from nltk import clean_html

from tickets.models import Ticket


class Command(BaseCommand):
    help = 'Get new tickets submitted via email'
    args = ''

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            m = imaplib.IMAP4_SSL(settings.IMAP_IP)
            m.login(settings.EMAIL_TICKET_USER, settings.EMAIL_TICKET_PASSWORD)
            m.select()
        except Exception, e:
            mail_admins('help.water error: Unable to login via IMAP', e)
            return

        try:
            typ, msg_nums = m.search(None, 'ALL')
        except Exception, e:
            mail_admins('help.water error: Unable to get %s Inbox' % settings.EMAIL_TICKET_USER, e)

        for num in msg_nums[0].split():
            try:
                typ, data = m.fetch(num, '(RFC822)')
                mail_body = quopri.decodestring(data[0][1])
                mes = email.message_from_string(mail_body)
                full_name, email_address = email.utils.parseaddr(mes.get('From'))
                subject = mes.get('Subject', 'N/A')
                mes_text = clean_html(mes.get_payload())
            except Exception, e:
                mail_admins('help.water error: Error with email sync', e)
                continue

            try:
                user = User.objects.get(email=email_address.lower())
            except User.DoesNotExist:
                name_list = full_name.split(' ', 1)
                try:
                    first_name = name_list[0]
                except IndexError:
                    first_name = 'First'
                try:
                    last_name = name_list[1]
                except IndexError:
                    first_name = 'Last'

                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email_address.lower()
                )
                user.set_unusable_password()
                user.save()

            ticket = Ticket(
                author=user,
                user=user,
                title=subject,
                description=mes_text,
            )
            ticket.save()

            try:
                m.store(num, '+FLAGS', '\\Deleted')
            except Exception, e:
                mail_admins('help.water error: Error with email delete', e)

        m.close()
        m.logout()

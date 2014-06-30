import ldap

from django.contrib.auth import get_user_model
from django.conf import settings

from custom.models import Department


class LDAPBackend(object):
    """
    Authenticates against Active Directory server via LDAP
    """
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        username = username.split('@')[0]
        try:
            active_directory_username = '%s@water.org' % username
            username = username.lower()
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            conn = ldap.initialize(settings.LDAP_ADDRESS)
            conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            conn.start_tls_s()
            conn.simple_bind_s(active_directory_username, password)
            ldap_search = conn.search_ext_s(
                'DC=waterpartnersint,DC=local',
                ldap.SCOPE_SUBTREE,
                filterstr='sAMAccountName=%s' % username
            )

            first_name = ldap_search[0][1]['givenName'][0]
            last_name = ldap_search[0][1]['sn'][0]
            email = ldap_search[0][1]['mail'][0]

            try:
                ldap_department = ldap_search[0][1]['department'][0]
            except:
                ldap_department = None

            if ldap_department:
                try:
                    department = Department.objects.get(title=ldap_department)
                except Department.DoesNotExist:
                    department = Department(
                        title=ldap_department,
                    )
                    department.save()

            User = get_user_model()

            try:
                user = User.objects.get(email=email.lower())
                user.first_name = first_name
                user.last_name = last_name
                user.email = email.lower()
                if ldap_department:
                    user.department = department
                user.set_unusable_password()
                user.save()
            except User.DoesNotExist:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    email=email.lower(),
                )
                if ldap_department:
                    user.department = department
                user.set_unusable_password()
                user.save()
            conn.unbind()
            return user

        except ldap.INVALID_CREDENTIALS:
            conn.unbind()
            return None
        except:
            conn.unbind()
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

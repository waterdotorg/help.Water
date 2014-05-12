import simplejson

from django import http
from django.contrib.auth.decorators import login_required

from tickets.models import Ticket
from watch.forms import WatchTicketForm


@login_required
def watch_ticket_ajax(request):
    response_data = {}
    response_data['success'] = False
    response_data['errors'] = ''

    if not request.method == 'POST' or not request.is_ajax():
        return http.HttpResponseForbidden('Forbidden.')

    data = request.POST
    files = request.FILES
    form = WatchTicketForm(data, files, user=request.user)

    if form.is_valid():
        t = Ticket.objects.get(pk=form.cleaned_data.get('ticket_id'))

        if request.user in t.watchers.all():
            t.watchers.remove(request.user)
        else:
            t.watchers.add(request.user)

        response_data['success'] = True
    else:
        response_data['errors'] = dict((k, map(unicode, v))
                                       for (k, v) in form.errors.iteritems())

    return http.HttpResponse(simplejson.dumps(response_data),
                             mimetype='application/json; charset=UTF-8')

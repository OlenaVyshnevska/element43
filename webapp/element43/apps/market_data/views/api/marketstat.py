# numpy processing imports
import numpy as np

# Template and context-related imports
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

# Aggregation
from django.db.models import Min
from django.db.models import Max
from django.db.models import StdDev

# market_data models
from apps.market_data.models import Orders
from apps.market_data.models import OrderHistory
from apps.market_data.models import ItemRegionStat

def legacy_marketstat(request):
    """
    This will match the Eve-central api for legacy reasons
    
    TODO: multiple regions submitted, multiple typeIDs, better error handling
    """
    
    params = {}
    # parse GET parameters and put them into a dict to make life easier
    for key in request.GET.iterkeys():
        params[key]=request.GET.getlist(key)
        
    stats = ItemRegionStat.objects.get(invtype_id=params['typeid'][0],
                                          mapregion_id=params['regionlimit'][0])
    buystats = Orders.active.filter(invtype_id=params['typeid'][0],
                                     mapregion_id=params['regionlimit'][0],
                                     is_bid=True).aggregate(Min('price'), Max('price'), StdDev('price'))
    sellstats = Orders.active.filter(invtype_id=params['typeid'][0],
                                     mapregion_id=params['regionlimit'][0],
                                     is_bid=False).aggregate(Min('price'), Max('price'), StdDev('price'))
    
    rcontext = RequestContext(request, {'params':params,
                                        'stats':stats,
                                        'buystats':buystats,
                                        'sellstats':sellstats})
        
    return render_to_response('market/api/legacy_marketstat.haml', rcontext, mimetype="application/xhtml+xml")
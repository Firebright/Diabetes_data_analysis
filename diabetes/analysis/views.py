# CDN link to jQuery
# http://code.jquery.com/jquery-1.7.2.min.js

from django.shortcuts import render_to_response
from django.template import RequestContext
from analysis.models import Events
#from chartit import PivotDataPool, PivotChart, DataPool, Chart


# Default Stats module homepage
def home(request):
    return render_to_response('base.html', {}, context_instance=RequestContext(request))


def summary_index(request):
    "Show the Apple 'Summary' User Action results"
    summary_data = AppleWeeklySummary.merged.all()

    # Create a Datapool object for Chartit
    cdata = PivotDataPool(
        series=[{
            'options':{
                'source': AppleWeeklySummary.objects.all(),
                'categories': [
                    'week_beginning'
                ],
                },
            'terms':{
                'weekly_total': Sum('total_track_downloads')
            }
        }]
    )
    # Create a Chart object for Chartit
    pivcht = PivotChart(
        datasource = cdata,
        series_options = [{
            'options':{
                'type':'column',
                'stacking':False,
                'yAxis': 0
            },
            'terms':[
                'weekly_total',
                ]
        }],
        chart_options = {
            'title':{'text':'Number of downloads per week for iTunes U'},
            'xAxis':{
                'title': {
                    'text':'Week Beginning'
                },
                'labels':{
                    'rotation': '0',
                    'step': '8',
                    'staggerLines':'2'
                }
            },
            'yAxis':[{
                'title': {
                    'text':'Download Count',
                    'rotation': '90'
                },
                'min':0
            }]
        }
    )

    return render_to_response('stats/apple/apple_summary.html', {
        'summary_data': summary_data,
        'cht':pivcht
    }, context_instance=RequestContext(request)
    )

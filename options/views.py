import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .command_config import command_config


def index(request):
    return render(
        request,
        'options/index.html',
        {
            'command_config': command_config,
        },
    )


# TODO: sudo, killall
@csrf_exempt
def api(request, *args, **kwargs):
    data = json.loads(request.body)
    section_name = data['section_name']
    command_id = data['command_id']
    input = data['input']
    command_data = command_config[section_name][command_id]
    command_template = command_data['command']
    input = command_data['stringify_input'](command_data['parse_input'](input))

    print('would run:')
    print(command_template.format(input))
    # TODO: output
    return HttpResponse('[]')

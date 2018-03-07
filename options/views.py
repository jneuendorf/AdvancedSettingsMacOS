from os import path
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .command_config import command_config
from .command import Command


PASSWORD_FILE_PATH = path.join(path.dirname(path.abspath(__file__)), 'password.txt')


def index(request):
    return render(request, 'options/index.html', {
        'command_config': command_config,
    })


@csrf_exempt
def store_password(request, *args, **kwargs):
    password = request.body.decode(encoding='UTF-8')
    try:
        with open(PASSWORD_FILE_PATH, "w") as password_file:
            password_file.write(password)
        return HttpResponse('true')
    except IOError as e:
        print('ERROR')
        print(e)
        return HttpResponse('false')


@csrf_exempt
def delete_password(request, *args, **kwargs):
    try:
        with open(PASSWORD_FILE_PATH, "w") as password_file:
            password_file.write('__none__')
        return HttpResponse('true')
    except IOError as e:
        print('ERROR')
        print(e)
        return HttpResponse('false')


# TODO: killall
@csrf_exempt
def api(request, *args, **kwargs):
    data = json.loads(request.body)
    section_name = data['section_name']
    command_id = data['command_id']
    input = data['input']

    section_data = command_config[section_name]

    meta_data = {
        'run_before': None,
        'run_after': None,
        **section_data.get('_meta', {})
    }

    status = 0
    messages = []

    if meta_data['run_before']:
        before_status, before_message = Command.run_meta(meta_data['run_before'])
        status = max(status, before_status)
        messages.append(before_message)

    command_data = section_data[command_id]
    command_status, command_message = Command.run(command_data, input)
    status = max(status, command_status)
    messages.append(command_message)

    if meta_data['run_after']:
        after_status, after_message = Command.run_meta(meta_data['run_after'])
        status = max(status, after_status)
        messages.append(after_message)

    return JsonResponse({
        'status': status,
        'message': '. '.join(messages),
    })

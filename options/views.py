from os import path
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .command_config import command_config


PASSWORD_FILE_PATH = path.join(path.dirname(path.abspath(__file__)), 'password.py')


def index(request):
    return render(
        request,
        'options/index.html',
        {
            'command_config': command_config,
        },
    )


@csrf_exempt
def store_password(request, *args, **kwargs):
    password = request.body.decode(encoding='UTF-8')
    try:
        with open(PASSWORD_FILE_PATH, "w") as password_file:
            password_file.write(f"password = '{password}'")
        return HttpResponse('true')
    except IOError as e:
        print('ERROR')
        print(e)
        return HttpResponse('false')


@csrf_exempt
def delete_password(request, *args, **kwargs):
    try:
        with open(PASSWORD_FILE_PATH, "w") as password_file:
            password_file.write('password = None')
        return HttpResponse('true')
    except IOError as e:
        print('ERROR')
        print(e)
        return HttpResponse('false')


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

    if command_data.get('sudo', False):
        #########################################################
        from .password import password

        # Try to use password from password file.
        if password is not None:
            password_command = f'password="{password}"'
        # Ask for password.
        else:
            password_command = 'password="$(osascript -e \'Tell application "System Events" to display dialog "Password:" default answer "" with hidden answer\' -e \'text returned of result\' 2>/dev/null)" &&'
        command_template = f'{password_command} echo "$password" | sudo -S {command_template}'
        # command_template = f"echo '{data['password']}' | sudo -S {command_template}"

    print('would run:')
    print(command_template.format(input))
    # TODO: output
    return HttpResponse('[]')

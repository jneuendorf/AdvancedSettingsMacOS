# import json
# import os
import subprocess

class Command():

    @classmethod
    def run(self, command_data, input):
        input = command_data['stringify_input'](command_data['parse_input'](input))
        command = self._get_command_string(command_data).format(input)
        return self._run(command)

    @classmethod
    def run_meta(self, command_data):
        command = self._get_command_string(command_data)
        return self._run(command)


    @classmethod
    def _get_command_string(self, command_data):
        command_template = command_data['command']
        if command_data.get('sudo', False):
            return f'{self._get_password_command()} && echo "$password" | sudo -S {command_template}'
        # else:
        return command_template

    @classmethod
    def _get_password_command(self):
        '''Returns a bash command for setting the password.
        If the password is set in 'password.py' that password is preferred.
        Otherwise the user is prompted for a password.'''

        from .password import password
        # Try to use password from password file.
        if password is not None:
            return f'password="{password}"'
        # else: Ask for password.
        # see https://apple.stackexchange.com/a/23514
        return 'password="$(osascript -e \'Tell application "System Events" to display dialog "Password:" default answer "" with hidden answer\' -e \'text returned of result\' 2>/dev/null)"'

    @classmethod
    def _run(self, command):
        print(f'running: {command}')
        try:
            response = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
            )
            success = True
        except subprocess.CalledProcessError as error:
            success = error.returncode
            response = error.output
        return success, response.decode("utf-8")

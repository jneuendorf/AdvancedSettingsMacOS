import subprocess


class Command():

    @classmethod
    def run(self, command_data, input):
        input = command_data['stringify_input'](command_data['parse_input'](input))
        command = self._get_command_string(command_data).format(input)
        return self._run_raw(command)

    @classmethod
    def run_meta(self, command_data):
        command = self._get_command_string(command_data)
        return self._run_raw(command)

    @classmethod
    def run_state(self, command_string, command_data):
        command = self._regarding_sudo(
            command_data,
            command_string,
            require_file_password=True,
        )
        return self._run_raw(command)


    @classmethod
    def _get_command_string(self, command_data):
        return self._regarding_sudo(command_data, command_data['command'])

    @classmethod
    def _regarding_sudo(self, command_data, command_string, require_file_password=False):
        if command_data.get('sudo', False):
            return f'{self._get_password_command(require_file_password)} && echo "$password" | sudo -S {command_string}'
        return command_string

    @classmethod
    def _get_password_command(self, require_file_password):
        '''Returns a bash command for setting the password.
        If the password is set in 'password.py' that password is preferred.
        Otherwise the user is prompted for a password.'''

        from .password import password

        if require_file_password and password is None:
            raise ValueError('No password in \'password.py\'.')

        # Try to use password from password file.
        if password is not None:
            return f'password="{password}"'
        # else: Ask for password.
        # see https://apple.stackexchange.com/a/23514
        return 'password="$(osascript -e \'Tell application "System Events" to display dialog "Password:" default answer "" with hidden answer\' -e \'text returned of result\' 2>/dev/null)"'

    @classmethod
    def _run_raw(self, command):
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

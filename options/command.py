# import json
# import os
import subprocess

class Command():
    @classmethod
    def run(self, command):
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

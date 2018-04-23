import socket
import sys
import shelve
import datetime
from collections import OrderedDict


class Queues:
    def __init__(self, timeout):
        self._queues = dict()
        self._filename = 'log'
        self._id_counter = 0
        self._timedelta = datetime.timedelta(minutes=timeout)
        self._write_err_msg = "something was wrong when writing to file..."

    def add_command(self, queue_name, length, data):
        if queue_name not in self._queues:
            self._queues[queue_name] = OrderedDict()

        task_id = str(self._id_counter)
        running = False
        time_get = None
        task_params = [length, data, running, time_get]
        self._queues[queue_name][task_id] = task_params
        self._id_counter += 1
        if not self.save_changes_to_file():
            raise IOError(self._write_err_msg)

        return task_id

    def get_command(self, queue_name):
        if queue_name not in self._queues:
            return None

        time_now = datetime.datetime.now()
        for task_id, task_params in self._queues[queue_name].items():
            if not task_params[2]:
                task_params[2] = True
                task_params[3] = time_now
                if not self.save_changes_to_file():
                    raise IOError(self._write_err_msg)

                return ' '.join([task_id, task_params[0], task_params[1]])

        return None

    def ack_command(self, queue_name, task_id):
        if queue_name not in self._queues:
            raise ValueError("{} doesn't exist".format(queue_name))
        if self.in_command(queue_name, task_id) == 'NO':
            status = "NO"
        else:
            self.check_timeout(queue_name, task_id)
            if not self._queues[queue_name][task_id][2]:
                status = "NO"
            else:
                self._queues[queue_name].pop(task_id)
                status = "YES"

        if not self.save_changes_to_file():
            raise IOError(self._write_err_msg)
        return status

    def in_command(self, queue_name, task_id):
        if queue_name not in self._queues:
            raise ValueError("{} doesn't exist".format(queue_name))
        if task_id in self._queues[queue_name].keys():
            status = "YES"
        else:
            status = "NO"

        if not self.save_changes_to_file():
            raise IOError(self._write_err_msg)
        return status

    def check_timeout(self, queue_name, task_id):
        task_time_delta = datetime.datetime.now() - self._queues[queue_name][task_id][3]
        if task_time_delta > self._timedelta:
            self._queues[queue_name].pop(task_id)

    def save_changes_to_file(self):
        try:
            with shelve.open(self._filename, 'n') as log_file:
                    for queue in self._queues:
                        log_file[queue] = self._queues[queue]
        except IOError:
            return False

        return True

    def read_file(self):
        try:
            with shelve.open(self._filename, 'c') as log_file:
                    for queue in log_file.keys():
                        self._queues[queue] = log_file[queue]
        except IOError:
            return False

        return True


def run(port=8080, timeout=5, ip_addr='0.0.0.0'):
    max_command_length = 5000000
    queues = Queues(timeout)
    queues.read_file()
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((ip_addr, port))
    connection.listen(10)
    while True:
        current_connection, address = connection.accept()
        command = current_connection.recv(max_command_length)
        response = command_processing(command, queues)
        send_and_close(current_connection, response)


def command_processing(command, queues):
    command = command.decode('utf-8')
    if not check_command(command):
        return None

    commands = {'ADD': queues.add_command, 'GET': queues.get_command,
                'ACK': queues.ack_command, 'IN': queues.in_command}
    parsed_command = command.split()
    method_name = parsed_command[0]
    params = parsed_command[1:]
    response = commands[method_name](*params)
    b_response = response.encode()
    return b_response


def check_command(command):
    params = command.split()
    try:
        if params[0] not in ['GET', 'ADD', 'ACK', 'IN']:
            return False
        if params[0] == 'GET' and len(params) != 2:
            return False
        if params[0] == 'IN' and len(params) != 3:
            return False
        if params[0] == 'ACK' and len(params) != 3:
            return False
        if params[0] == 'ADD' and len(params) != 4:
            return False
        return True
    except (ValueError, IndexError):
        return False


def send_and_close(current_connection, data):
    current_connection.send(data)
    current_connection.shutdown(1)
    current_connection.close()


def parse_args(_args):
    try:
        if not 0 <= int(_args[0]) <= 65535:
            raise ValueError
        _args[0] = int(_args[0])

        if len(_args) > 1:
            if not 1 <= int(_args[1]) <= 10000:
                raise ValueError
            _args[1] = int(_args[1])

        if len(_args) > 2:
            ip_addr = _args[2].split('.')
            if len(ip_addr) != 4 or not all([0 <= int(i) <= 255 for i in ip_addr]):
                raise ValueError

        return _args
    except ValueError:
        print("Incorrect params\nUsage: python3 server.py [port] [timeout] [ip_address]")
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        run()
    else:
        args = parse_args(sys.argv[1:])
        if args:
            run(*args)

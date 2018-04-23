from unittest import TestCase
from server import Queues
from collections import OrderedDict
import time
import socket
import subprocess
import datetime


class QueuesTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python3', 'server.py', '8080'])
        time.sleep(0.5)
        self.queues = Queues(5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def test_init(self):
        expected_results = (dict(), 'log', 0, datetime.timedelta(minutes=5))
        real_results = (self.queues._queues, self.queues._filename,
                        self.queues._id_counter, self.queues._timedelta)
        self.assertEqual(expected_results, real_results)

    def test_check_timeout(self):
        test_time1 = datetime.datetime.now() - datetime.timedelta(minutes=4)
        self.queues._queues[0] = OrderedDict()
        self.queues._queues[0][0] = ['5', '12345', False, test_time1]
        self.queues.check_timeout(0, 0)
        self.assertEqual(len(self.queues._queues[0]), 1)

        test_time2 = datetime.datetime.now() - datetime.timedelta(minutes=5)
        self.queues._queues[0][0] = ['5', '12345', False, test_time2]
        self.queues.check_timeout(0, 0)
        self.assertEqual(len(self.queues._queues[0]), 0)

    def test_add_command(self):
        id1 = self.queues.add_command('ABC', '6', '123456')
        id2 = self.queues.add_command('BCD', '7', '1234567')
        id3 = self.queues.add_command('ABC', '5', '12345')
        q1 = self.queues._queues['ABC']
        q2 = self.queues._queues['BCD']
        ids = [id1, id2, id3]
        self.assertEqual(ids, ['0', '1', '2'])
        self.assertEqual(q1, OrderedDict([('0', ['6', '123456', False, None]),
                                          ('2', ['5', '12345', False, None])]))
        self.assertEqual(q2, OrderedDict([('1', ['7', '1234567', False, None])]))

    def test_in_command(self):
        task_id1 = self.queues.add_command('ABC', '6', '123456')
        task_id2 = self.queues.add_command('ABCD', '4', '1234')
        self.assertEqual(self.queues.in_command('ABC', task_id1), "YES")
        self.assertEqual(self.queues.in_command('ABCD', task_id1), "NO")
        self.assertEqual(self.queues.in_command('ABC', task_id2), "NO")

    def test_ack_command(self):
        task_id = self.queues.add_command('ABC', '6', '123456')
        self.queues._queues['ABC'][task_id][3] = datetime.datetime.now()
        self.assertEqual(self.queues.ack_command('ABC', task_id), "NO")

    def test_get_command(self):
        task_id = self.queues.add_command('ABC', '6', '123456')
        self.assertEqual(self.queues.get_command('ABC'), task_id + ' 6' + ' 123456')
        self.assertEqual(self.queues.get_command('ABC'), None)


class ServerBaseTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python3', 'server.py'])
        self._ip_addr = '127.0.0.1'
        self._port = 8080
        time.sleep(0.5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 8080))
        s.send(command)
        data = s.recv(5000000)
        s.close()
        return data

    def test_base_scenario(self):
        task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))

        self.assertEqual(task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'IN 1 ' + task_id))

    def test_two_tasks(self):
        first_task_id = self.send(b'ADD 1 5 12345')
        second_task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))

        self.assertEqual(first_task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))
        self.assertEqual(second_task_id + b' 5 12345', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + second_task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + second_task_id))

    def test_read_file(self):
        task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))

        self.tearDown()
        time.sleep(0.5)
        self.server = subprocess.Popen(['python3', 'server.py'])
        time.sleep(0.5)

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'IN 1 ' + task_id))


if __name__ == '__main__':
    unittest.main()
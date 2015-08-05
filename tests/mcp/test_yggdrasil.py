from __future__ import unicode_literals

import unittest

import mock

from spock.mcp.yggdrasil import YggAuth


@mock.patch('six.moves.urllib.request.Request')
@mock.patch('six.moves.urllib.request.urlopen')
class YggAuthRequestTest(unittest.TestCase):
    def test_request_is_done(self, urlopen, request):
        decode = urlopen.return_value.read.return_value.decode
        decode.return_value = '{"test": 1}'
        ygg = YggAuth()
        self.assertFalse(urlopen.called)
        self.assertFalse(request.called)
        res = ygg._ygg_req('/test', [{'a': 'b'}, 'c', 'd', 'e'])

        # First create the request
        request.assert_called_once_with(
            'https://authserver.mojang.com/test',
            '[{"a": "b"}, "c", "d", "e"]',
            '{"Content-Type": "application/json"}')

        # Then send it
        urlopen.assert_called_once_with(request.return_value)

        # Read the response
        self.assertTrue(urlopen.return_value.read.called)
        self.assertTrue(decode.called)

        self.assertEqual(res, {'test': 1})


@mock.patch('spock.mcp.yggdrasil.YggAuth._ygg_req')
class YggAuthTest(unittest.TestCase):
    def setUp(self):
        self.ygg = YggAuth()
        self.assertFalse(self.ygg.username)
        self.assertFalse(self.ygg.password)
        self.assertFalse(self.ygg.client_token)
        self.assertFalse(self.ygg.access_token)

    def test_authenticate_success(self, ygg_req):
        ygg_req.return_value = {'accessToken': 'myaccess',
                                'clientToken': 'mytoken'}

        res = self.ygg.authenticate('user', 'pass', 'clienttoken')

        ygg_req.assert_called_once_with('/authenticate', {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
            'username': 'user',
            'password': 'pass',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, 'user')
        self.assertEqual(self.ygg.password, 'pass')
        self.assertEqual(self.ygg.client_token, 'mytoken')
        self.assertEqual(self.ygg.access_token, 'myaccess')

        self.assertEqual(res, ygg_req.return_value)

    def test_authenticate_failure(self, ygg_req):
        ygg_req.return_value = {'error': 1}

        res = self.ygg.authenticate('user', 'pass', 'clienttoken')

        ygg_req.assert_called_once_with('/authenticate', {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
            'username': 'user',
            'password': 'pass',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, 'user')
        self.assertEqual(self.ygg.password, 'pass')
        self.assertEqual(self.ygg.client_token, 'clienttoken')
        self.assertEqual(self.ygg.access_token, None)

        self.assertEqual(res, ygg_req.return_value)

    def test_refresh_success(self, ygg_req):
        pass

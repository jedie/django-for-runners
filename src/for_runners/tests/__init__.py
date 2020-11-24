#
# Hardcore Monkey patch to find not mocked requests ;)
# But this will also break selenium tests, too.
#
# import socket
#
# class SocketMock:
#     def __call__(self, *args, **kwargs):
#         raise NotImplementedError(
#             'Socket is monkeypatched in Tests!'
#         )
#
# socket.socket = SocketMock()

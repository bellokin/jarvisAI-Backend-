# import socketio

# # Initialize Socket.IO server
# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# # Wrap the Socket.IO server with an ASGI app
# # This will serve requests on `/socket.io/` by default
# sio_app = socketio.ASGIApp(sio)

# # if __name__ == '__main__':
# #     from wsgiref.simple_server import make_server
# #     server = make_server('0.0.0.0', 8000, sio_app)
# #     server.serve_forever()

# # Define Socket.IO event handlers
# @sio.event
# async def connect(sid, environ):
#     print(f"Client connected: {sid}")

# @sio.event
# async def disconnect(sid):
#     print(f"Client disconnected: {sid}")

# @sio.event
# async def message(sid, data):
#     print(f"Message from {sid}: {data}")
    
#     # Validate and broadcast
#     if data in ["Yes", "No"]:
#         await sio.emit("signal", data)
#     else:
#         print(f"Invalid message: {data}")

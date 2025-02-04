import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class MyWebSocketConsumer(WebsocketConsumer):
    def connect(self):
        # Accept the WebSocket connection
        self.accept()

        # Add the connection to a group (e.g., "energy_management_group")
        async_to_sync(self.channel_layer.group_add)(
            "energy_management_group",  # Group name
            self.channel_name  # This channel's unique name
        )

        # Send an initial state to the client
        self.send_switch_control('No')  # Default state

    def disconnect(self, close_code):
        # Remove the connection from the group upon disconnection
        async_to_sync(self.channel_layer.group_discard)(
            "energy_management_group",
            self.channel_name
        )

    def receive(self, text_data):
        try:
            # Parse the incoming JSON data
            data = json.loads(text_data)

            # Handle commands (e.g., "turn_on" or "turn_off")
            if 'action' in data:
                action = data['action']
                if action == 'turn_on':
                    # Broadcast to the group
                    async_to_sync(self.channel_layer.group_send)(
                        "energy_management_group",
                        {
                            "type": "switch_control_message",  # Event type
                            "state": "Yes"  # Payload
                        }
                    )
                elif action == 'turn_off':
                    # Broadcast to the group
                    async_to_sync(self.channel_layer.group_send)(
                        "energy_management_group",
                        {
                            "type": "switch_control_message",
                            "state": "No"
                        }
                    )
                else:
                    self.send(text_data=json.dumps({'error': 'Unknown action'}))
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({'error': 'Invalid JSON received'}))

    def send_switch_control(self, state):
        """Send the current switch control state to the client."""
        self.send(text_data=json.dumps({
            'switch_control': state
        }))

    def switch_control_message(self, event):
        """Handle group messages and forward them to the WebSocket client."""
        state = event['state']
        self.send_switch_control(state)


class CurrentValuesConsumer(WebsocketConsumer):
    def receive(self, text_data=None, bytes_data=None):
        """Handle incoming WebSocket messages."""
        if text_data:
            try:
                print(f"Received data from ESP8266: {text_data}")  # Debugging

                # Parse incoming data
                data = json.loads(text_data)
                current = data.get("current")
                voltage = data.get("voltage")

                if current is not None and voltage is not None:
                    # Broadcast the current and voltage to all clients
                    CurrentValuesConsumer.broadcast_current_values(current=current, voltage=voltage)
                else:
                    print("Invalid data received. Missing 'current' or 'voltage'.")
            except json.JSONDecodeError:
                self.send(text_data=json.dumps({'error': 'Invalid JSON received'}))

    def connect(self):
        """Accept the WebSocket connection and add it to the group."""
        self.accept()

        # Add this WebSocket connection to the "current_values_group"
        async_to_sync(self.channel_layer.group_add)(
            "current_values_group",  # Group name
            self.channel_name  # Unique channel name
        )

        # Optionally send an initial message
        self.send_current_values({'current': 2.0, 'voltage': 2.0})  # Default state

    def disconnect(self, close_code):
        """Remove the WebSocket connection from the group."""
        async_to_sync(self.channel_layer.group_discard)(
            "current_values_group",
            self.channel_name
        )

    def send_current_values(self, data):
        """Send the current electrical values to the WebSocket client."""
        print(f"Sending data to client: {data}")
        self.send(text_data=json.dumps(data))

    def current_values_message(self, event):
        """
        Handle group messages. Forward data received via the channel layer
        to the WebSocket client.
        """
        current_data = event['current_data']
        self.send_current_values(current_data)

    @classmethod
    def broadcast_current_values(cls, current, voltage):
        print(f"Broadcasting current: {current}, voltage: {voltage}")  # Debugging
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "current_values_group",  # Group name
            {
                "type": "current_values_message",  # Event type
                "current_data": {"current": current, "voltage": voltage}
            }
        )

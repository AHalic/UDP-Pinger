# UDP-Pinger
An UDP Pinger implementation for the Network discipline

## Implementation
This implementation was made with Python and the [socket](https://docs.python.org/3/library/socket.html) package.
The client sends a ping message following the pattern `0000{packet number}{ping marker}{timestamp}SOPHIE DILHON`, and expects to receive the same message.
The following errors are treated:
  - Message has an invalid number
  - Message is not a pong
  - Message doesnt have the same content sent
  - Message doesnt have the same timestamp sent
  - Message is delayed
  - No message received (timeout)


## Execution 
To run the client, the server must be already running. In separe terminals, run the following commands (make sure to verify the host address in the client):
```
python3 Server.py
python3 ClientUDP.py host_address host_port number_of_packets
```

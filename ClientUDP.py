from socket import *
import time
import sys
import numpy as np


class ClientUDP:
    """
    Class representing a client that uses UDP protocol to send and receive messages

    `param` host: host to send messages (must be the same as the client)
    `param` port: port to send messages (must be different than the client's)
    `param` packages: number of packages to send
    """

    def __init__(self, host='127.0.0.1', port=30000, packages=10):
        super(ClientUDP, self).__init__()

        self.HOST = host
        self.PORT = port
        self.rtt_history = []
        self.start_history = []
        self.received = 0
        self.packages = packages
        self.socketUDP = socket(AF_INET, SOCK_DGRAM)
        self.server = (self.HOST, self.PORT)
        self.socketUDP.settimeout(1)

    def pong(self, i, time_start):
        """
        Receives a message from the server

        `param` i: sequence number of the message
        `param` time_start: time when the message was sent
        """
        try:
            # receives a 40 bytes message
            data, _ = self.socketUDP.recvfrom(40)
            rtt = abs((float(str(round(time.time_ns() / 1000))[-4:]) - float(data[6:10])) / 1000)

            data = data.decode()

            # check if message is valid, and decode it
            msg, delayed = self.check_message(data, rtt, i)

            print(msg)
            self.received += 1

            if delayed:
                self.pong(i, time_start)

            # if type(msg) is str:
            # elif type(msg) is float:
            #     # case where the message was delayed
            #     self.rtt_history.append(msg)

        except timeout:
            print("From " + str(self.HOST) + ":" + str(self.PORT) + ": udp_seq=" + str(i+1) +  " Connection time out")        
        except:
            print("From " + str(self.HOST) + ":" + str(self.PORT) + ": udp_seq=" + str(i+1) + " Destination Host Unreachable")
                

    def run_ping_pong(self):
        """
        Sends the messages to the server and receives it's responses
        The message must follow the pattern: 
            5 bytes: sequence number
            1 byte: 0 (ping) or 1 (pong)
            4 bytes: timestamp
            30 bytes: message ("SOPHIE DILHON")
        Prints the report at the end
        """

        for i in range(self.packages):
            # define message
            time_start = str(round(time.time_ns() / 1000))[-4:] # os ultimos 4 bytes
            self.start_history.append(time_start)
            message = ("0000" + str(i) + "0" + time_start + "SOPHIE DILHON").encode("utf-8")

            # send message (ping)
            self.socketUDP.sendto(message, self.server)

            # receive message (pong)
            self.pong(i, time_start)
                
        # print final rtt
        self.print_report()
        self.socketUDP.close()


    def check_message(self, data, rtt, seq_number, delay=False):
        """
        Checks if the message received is valid

        `param` data: message received (decoded)
        `param` rtt: round trip time
        `param` seq_number: sequence number of the message
        `param` delay: boolean indicating if the message was delayed

        `return` report to be printed according to the message received

        Error cases:
            - sequence number is not the same as the one sent (message was delayed)
            - message is not the same than the one sent
            - message is not a pong
            - message has a different timestamp than the sent
        """
        error_msg = "From " + str(self.HOST) + ":" + str(self.PORT) + ": udp_seq="


        if int(data[0:5]) > self.packages or int(data[0:5]) < 0:
            return (error_msg + str(int(data[0:5])+1) +  " Number Error " + "time=" + str(rtt), False)
        elif int(data[0:5]) != (seq_number) and not delay:
            # imprime o delay e recebe de novo
            msg, _ = self.check_message(data, rtt, seq_number, True)
            return (msg + " (Packet delay)", True)
        elif data[5] != "1":
            return (error_msg + str(int(data[0:5])+1) +  " Ping/Pong Error " + "time=" + str(rtt), False)
        elif data[10:23].upper() != "SOPHIE DILHON":
            return (error_msg + str(int(data[0:5])+1) +  " Message Error " + "time=" + str(rtt), False)
        elif data[6:10] != self.start_history[int(data[0:5])]:
            return (error_msg + str(int(data[0:5])+1) +  " Timestamp Error " + "time=" + str(rtt), False)
        else:
            self.rtt_history.append(rtt)
            return (str(len(data)) + " bytes from " + str(self.HOST) + ":" + str(self.PORT) + ": udp_seq=" + str(int(data[0:5])+1) +  " time=" + str(rtt), False)

    def print_report(self):
        """"
        Prints the report of the client
        """

        min_rtt = 0
        avg_rtt = 0
        max_rtt = 0
        std_rtt = 0

        if len(self.rtt_history) > 0:
            min_rtt = min(self.rtt_history)
            avg_rtt = np.mean(self.rtt_history)
            max_rtt = max(self.rtt_history)
            std_rtt = np.std(self.rtt_history)

        print("\n--- " + self.HOST + " ping statistics ---")
        print(f'{self.packages} packets transmitted, {self.received} received, {round(100*(1.0 - (self.received/self.packages))):.2f}% packet loss, {len(self.rtt_history)} consistent packet ')
        print(f'rtt min/avg/max/mdev = {min_rtt:.2f} / {avg_rtt:.2f} / {max_rtt:.2f} / {std_rtt:.2f} ms\n')



if __name__ == "__main__":
    host = '127.0.0.1'
    port = 30000
    packs = 10

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    if len(sys.argv) == 3:
        packs = int(sys.argv[3])

    print("Host: " + host)
    client = ClientUDP(host, port, packs)
    client.run_ping_pong()
import threading
import time
import random


class CovertChannel:
    def __init__(self):
        self.message = ""
        self.event_sender = threading.Event()
        self.event_receiver = threading.Event()

    def sender(self, bits):
        for bit in bits:
            print("Sending bit:", bit)
            send_bit(bit)
            self.event_receiver.set()
            self.event_sender.wait()
            self.event_sender.clear()

    def receiver(self, num_bits):
        received_message = ""
        for _ in range(num_bits):
            start_time = time.time()
            self.event_receiver.wait()
            time_taken = time.time() - start_time
            bit = receive_bit(time_taken)
            received_message += bit
            print("Received bit:", bit)
            self.event_sender.set()
            self.event_receiver.clear()
        print("Received message:", received_message)


def send_bit(bit):
    if bit == '0':
        time.sleep(random.uniform(0.1, 0.2))
    else:
        time.sleep(random.uniform(0.3, 0.4))


def receive_bit(time_taken):
    if time_taken < 0.2:
        return '0'
    else:
        return '1'


def main():
    covert_channel = CovertChannel()
    message = "10001010"
    print("Sending message:", message)
    sender_thread = threading.Thread(target=covert_channel.sender, args=(message,))
    receiver_thread = threading.Thread(target=covert_channel.receiver, args=(len(message),))

    sender_thread.start()
    receiver_thread.start()

    sender_thread.join()
    receiver_thread.join()


if __name__ == "__main__":
    main()

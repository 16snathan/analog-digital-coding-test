SHIVA NATHAN
May 6, 2022


# analog-digital-coding-test
The objective is to simulate sending a large number of SMS alerts, like for an emergency alert service. The simulation consists of three parts:
1. A producer that generates a configurable number of messages (default 1000) to random phone number. Each message contains up to 100 random characters.
2. A sender, who picks up messages from the producer and simulates sending messages by waiting a random period time distributed around a configurable mean. The sender also has a configurable failure rate.
3. A progress monitor that displays the following and updates it every N seconds (configurable):
    Number of messages sent so far
    Number of messages failed so far
    Average time per message so far
    
REQUIREMENTS:
Python 3.7.2

USE:
Import analog-test-main into your file
From analog-test-main you can import Producer, Monitor, Sender classes

TEST CASES:
Run analog-test-suite.py to automatically import analog-test-main.py and start a producer, monitor, and three senders. 

KNOWN FAULTS:
The implementation of collecting average wait time is incorrect. The fault in the implementation is still unknown.
The producer seems to generate a few extra messages(ie 1012 instead of 1000) but it is not clear if this is my fault or due to how the queue built-in class reports size.

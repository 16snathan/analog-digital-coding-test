from dataclasses import dataclass, field
import string
import random
import queue 
import threading #using threads instead of processes to share data more easily
import time

'''
WORKFLOW: 
Generate producer
Generate monitor
Generate senders
'''

# dataclass decorator makes it easier to quickly define a dataclass
@dataclass
class Producer:
    msg_count: int = 1000
    # Generates messages for Sender to pick up in queue of tuples: (number,message)
    generated_count = 0 #keeps count of how many messages have been put into queue
    msg_queue = queue.Queue(maxsize=msg_count) #Queue automatically implements thread safety
    
    def __post_init__(self): # dataclass post-init method is the last thing called by init
    #in this case we use it to start the thread
        self.producerThread = threading.Thread(target=self.main)
        self.producerThread.start()
    
    # return strings of random size (up to 100 chars) composed of random printable characters 
    def generateMessage(self):
        # generates randomly-sized list of random characters and concatenates it
        size = random.randint(1,100) 
        msgArray = random.choices(population=string.printable, k=size) 
        return ''.join(msgArray) 
    
    def incrementGeneratedCount(self,n=1):
        self.generated_count += n
        
    # return string of randomly generated phone number: "###-###-####"
    def generatePhoneNumber(self):
        areaCode = ''.join(random.choices(population=string.digits,k=3))
        middleCode = ''.join(random.choices(population=string.digits,k=3))
        endCode = ''.join(random.choices(population=string.digits,k=4))
        return '-'.join([areaCode,middleCode,endCode])

    def isQueueEmpty(self):
        return (self.msg_queue.qsize() <= 0)

    def isQueueFull(self):
        return (self.msg_queue.qsize() >= self.msg_count)

    #generates single message tuple and adds it to queue. Returns TRUE if successful and FALSE otherwise
    def putMsg(self): 
        assert(self.msg_queue.full() == False)
        msgTuple = (self.generatePhoneNumber(),self.generateMessage())
        try:
            self.msg_queue.put(msgTuple)
            return True
        except:
            return False

    # Pops message tuple from queue. Returns tuple: (number,message)
    def getMsg(self):
        assert(self.msg_queue.empty() == False)
        try:
            return self.msg_queue.get()
        except:
            return None

    #adds messages to queue until it is full
    def fillProducerQueue(self):
        while not self.isQueueFull():
            self.putMsg()

    def main(self): #Primary loop. Generates messages and populates reader queue with them
        #Ensure that producer has been given appropriate number of messages
        if (self.msg_count == None):
            print("Producer cannot generate infinite messages.")
            return -1
        if (self.msg_count <= 1):
            print("Producer must generate at least 1 message to send.")
            return -1
        # while queue is not full or not all messages have been generated, try to populate queue
        # print("Producer now generating messages...")
        while (self.generated_count < self.msg_count) or (not self.isQueueFull()):
            self.putMsg()
            self.incrementGeneratedCount()
            time.sleep(0.01) #brief sleep to allow other threads to access msg queue
        print("Producer has generated all {} messages".format(self.generated_count))
                
                


@dataclass
class Monitor():
    update_period: float = 1.0 # period between refreshing system counts
    # Monitors progress of Producer and Senders
    sender_count = 0 #updated by each sender listening to monitor
    success_count = 0 # int number of messages sent successfully
    fail_count = 0 # int number of messages that fail to send
    average_wait = 0.0 # float in seconds
    monitor_lock = threading.Lock() # controls access to writing to counts
    
    def __post_init__(self):
        self.run() #call monitor.run() to start monitor
        
    def incrementSenderCount(self,n = 1):
        self.sender_count += n
        
    def getSenderCount(self):
        return self.sender_count
    
    def updateMonitorSuccess(self,n):
        self.success_count += n
        
    def updateMonitorFailures(self,n):
        self.fail_count += n
        
    def updateMonitorAvgWait(self,n):
        cumulative_wait = (self.average_wait * self.sender_count)
        cumulative_wait += n
        self.average_wait += cumulative_wait / self.sender_count
    
    def getUpdatePeriod(self):
        return self.update_period
    
    def updateDisplay(self): #update display on loop with period self.update_period
        try:
            with self.monitor_lock:
                print("Number of messages sent: {}".format(self.success_count))
                print("Number of messages failed: {}".format(self.fail_count))
                print("Average wait time between messages: {:.2f} seconds".format(self.average_wait))
        finally:
            threading.Timer(interval=self.update_period,function=self.updateDisplay).start()

    
    def run(self): #Primary loop. Updates display every few seconds
        if self.update_period < 1.0:
            print("Monitor cannot update faster than one second at a time!")
            return -1
        print("Monitor main() started!")
        self.updateDisplay()
        

@dataclass
class Sender: 
    monitor: Monitor = None #monitor object to send to
    producer: Producer = None #producer object to listen to
    failure_rate: float = 0.25 #proportion from 0 to 1
    mean_wait: float = 1.0 #average wait time in seconds
    # Each sender runs a thread that: 
    # checks the producer for a message, retrieves it and tries to send it,
    # then reports to its monitor if it successfully sent the message
    msgTuple = None #used to report messages retrieved from producer
    sigma_wait = mean_wait / 3 #standard deviation of wait time in seconds, arbitrarily set as 1/3 of mean
    success_count = 0 # number of successfully transmitted messages
    failure_count = 0 # number of failed transmitted messages
    
    def __post_init__(self): # dataclass post-init method is the last thing called by init
    #in this case we use it to start the thread
        self.senderThread = threading.Thread(target=self.main)
        self.senderThread.start()
        
    def getMessage(self): #try to get message from producer queue
        try:
            msgTuple = self.producer.getMsg()
            return msgTuple
        except:
            return None
    
    # return randomly generated wait time around mean
    def getWaitTime(self,mean,stdev):
        waitTime = 0
        while (waitTime <= 0): waitTime = random.normalvariate(mean, stdev)
        return waitTime
   
    # returns TRUE if message sends successfully and FALSE otherwise
    def sendMessage(self):
        # simulate trying to send a message
        (number,msg) = self.msgTuple
        # print("trying to send message with {} chars to {}".format(len(msg),number))
        return (random.random() < self.failure_rate)
    
    def resetSenderMetrics(self):
        self.success_count = 0
        self.failure_count = 0
    
    def incrementSuccessCount(self):
        self.success_count += 1
    
    def getSuccessCount(self):
        return self.success_count
    
    def incrementFailureCount(self):
        self.failure_count += 1

    def getFailureCount(self):
        return self.failure_count
        
    def main(self): #Primary loop. Retrieves message from producer queue, tries to send it, reports to monitor 
        # ensure all parameters are valid 
        # print("Sender main() started!")
        if (self.monitor == None) or (self.producer == None): 
            print ("Sender needs a monitor parameter to report to and producer parameter to listen to")
            return -1
        if (self.failure_rate < 0.0 or self.failure_rate > 1.0):
            print ("Failure rate must be a float in range [0,1)")
            return -1
        if (self.mean_wait < 1.0):
            print ("Sender needs at least 1 second of wait time to send messages properly")
            return -1
         # add sender to monitor list and determine max lock timeout
        with self.monitor.monitor_lock:
            self.monitor.incrementSenderCount()
            self.resetSenderMetrics()
            timeoutPeriod = self.monitor.getUpdatePeriod() 
            # print("Sender {} operating with timeout {}".format(self.monitor.getSenderCount(),timeoutPeriod))
        # BEGIN main loop
        while True:
            # try to get message
            self.msgTuple = self.getMessage() 
            # wait for random time to send message
            if (self.msgTuple != None):
                sleepTime = self.getWaitTime(self.mean_wait,self.sigma_wait)
                time.sleep(sleepTime)
                # try to send message and update sender success / failure count
                if (self.sendMessage() == True): self.incrementSuccessCount() 
                else: self.incrementFailureCount()
                # Try to acquire monitor lock 
                try:
                    monitorLockAcquired = self.monitor.monitor_lock.acquire(timeout=timeoutPeriod)
                    if monitorLockAcquired:
                    # If lock is acquired, update the monitor count and reset the sender count
                        senderSuccessCount = self.getSuccessCount()
                        senderFailureCount = self.getFailureCount()
                        self.monitor.updateMonitorSuccess(senderSuccessCount)
                        self.monitor.updateMonitorFailures(senderFailureCount)
                        self.monitor.updateMonitorAvgWait(sleepTime)
                        self.resetSenderMetrics()
                finally: #otherwise avoid blocking and proceed with loop again until able to add values
                    if monitorLockAcquired:
                        self.monitor.monitor_lock.release()
        # END main loop
        self.senderThread.join()
    
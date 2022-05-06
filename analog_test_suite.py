from analog_test_main import Producer, Monitor, Sender

producer = Producer()
monitor = Monitor(5.0)
sender1 = Sender(monitor,producer)
sender2 = Sender(monitor,producer,failure_rate=0,mean_wait=3)
sender3 = Sender(monitor,producer,failure_rate=0,mean_wait=6)

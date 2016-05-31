import multiprocessing
import logging
import sys
import time
import argparse

from operator import itemgetter

from streamer import Streamer, Status

TIMEOUT_PERIOD = 60
NUM_WORKERS = 10

class Worker(multiprocessing.Process):

    def __init__(self, id, queue, logger):
        multiprocessing.Process.__init__(self)
        self.id = id
        self.queue = queue
        self.byte_count = 0
        self.status = Status.FAILURE
        self.logger = logger
    
    def run(self):
        end_time = 0
        try:
            fake_stream = Streamer()
            # UNCOMMENT the following debug messages to check if the worker reports stream statistics correctly. 
            # to make sure we do not mess up the stream state.
            # self.logger.debug( "Stream: id: {}, outcome: {}".format(self.id, fake_stream.outcome.name))
            while True:
                if fake_stream.getNext() == 'x' and fake_stream.getNext() == 'A' and fake_stream.getNext() == 'd':
                    # self.logger.debug( "Successful Stream: id: {}, outcome: {}".format(self.id, fake_stream.outcome.name))
                    self.byte_count += 1
                    end_time = time.time()
                    self.status = Status.SUCCESS
                    break
                self.byte_count += 1

        except Exception as e:
            self.logger.error("Worker {}: Failed to process stream. Exception: {}, {}".format(self.id, type(e).__name__, e.args))
            self.status = Status.FAILURE
            self.byte_count = 0
            
        self.queue.put((self.id, end_time, self.byte_count, self.status))
        self.status
        
    def _get_id(self):
        return self.id

if __name__ == '__main__':

    multiprocessing.log_to_stderr(logging.DEBUG)
    mlogger = multiprocessing.get_logger()
    mlogger.setLevel(logging.ERROR)
    
    logging.basicConfig(format="")
    logger = logging.getLogger("worker")
    logger.setLevel(logging.DEBUG)
    
    results = multiprocessing.Queue()
    
    procs = []
    timed_out_procs = []
    pretty_log=[]

    total_byte_cnt_successful = 0
    total_elapsed_successful = 0
    total_count_successful = 0


    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store', dest='timeout', default=60, 
                        help='timeout in seconds')
    parsed = parser.parse_args()
    TIMEOUT_PERIOD=int(parsed.timeout)

    start = time.time()
    
    for i in range(NUM_WORKERS):
        p = Worker(i+1, results, mlogger)
        procs.append(p)
        p.start()

    while time.time() - start <= TIMEOUT_PERIOD:
        if any(p.is_alive() for p in procs):
            time.sleep(.1)  # Just to avoid hogging the CPU
        else:
            # All the processes are done, break now.
            break
    else:
        for p in procs:
            if(p.is_alive()): # If a process is alive at this point then the stream has timed out
                p.terminate()
                timed_out_procs.append(p)
            
            
    while True:
        if results.empty(): # We have parsed all the successful/failure streams.
            break
        else:
            result = results.get() 
            elapsed = (result[1] - start)*1000 if result[1]> 0 else 0
            byte_count = result[2]
            status = Status(result[3]).name
            pretty_log.append((elapsed, byte_count, status, "Worker[{}]: [Elapsed]: {:.2f}ms [byte_count]: {} [status]: {}".format(result[0],  elapsed, byte_count, status)))
     
     # All of the logic with the pretty_log is simply to print the log in descending order of [elapsed]
    for p in timed_out_procs:
        pretty_log.append((0,0, Status.TIMEOUT.name, "Worker[{}]: [Elapsed]: {:.2f}ms [byte_count]: {} [status]:{}".format(p._get_id(), 0, 0, Status.TIMEOUT.name)))
    
    pretty_log = sorted(pretty_log, key=itemgetter(0), reverse=True)
    
    for l in pretty_log:
        logger.debug(l[3])
        if l[2] == Status.SUCCESS.name:
            total_count_successful += 1
            total_byte_cnt_successful += l[1]
            total_elapsed_successful += l[0]
            
    if total_count_successful > 0:            
        logger.debug("AVERAGE: Successful: {} [Elapsed]: {:.2f} [byte_count]: {:.2f}".format(total_count_successful, total_elapsed_successful/total_count_successful, total_byte_cnt_successful/total_count_successful))  

    for p in procs:
       p.join()

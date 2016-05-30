import multiprocessing
import logging
import sys
import time

from streamer import streamer

def worker(id, queue):
    byte_count = 0
    
    fake_stream = streamer()    
    while True:
        if fake_stream.getNext() == 'x' and fake_stream.getNext() == 'A' and fake_stream.getNext() == 'd':
            byte_count += 1
            break
        byte_count += 1
        
    end_time = time.time()
    queue.put((id, end_time, byte_count))

if __name__ == '__main__':
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.ERROR)
    
    results = multiprocessing.Queue()
    
    procs = []
    
    TIMEOUT = 5 
    start = time.time()
    
    for i in range(10):
        p = multiprocessing.Process(target=worker, args=(i, results,))
        procs.append(p)
        p.start()
        
 
    while time.time() - start <= TIMEOUT:
        if any(p.is_alive() for p in procs):
            time.sleep(.1)  # Just to avoid hogging the CPU
        else:
            # All the processes are done, break now.
            break
    else:
        # We only enter this if we didn't 'break' above.
        print("timed out, killing all processes")
        for p in procs:
            p.terminate()
            p.join()
            
    for i in range(10):
        result = results.get() 
        print "Worker[{}]: [Elapsed]: {}ms [byte_count]: {}".format(result[0], (result[1] - start)*1000, result[2])

        
    
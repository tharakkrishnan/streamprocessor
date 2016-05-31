# StreamProcessor

## Installation and usage

This program requires the "enum" module that is part of python 3.4 and requires a version of python that is 3.4 or greater. If the "enum" module is not installed,
please install it by invoking:
        $ pip install enum
Alternatively, it can also be installed by invoking
        $ cd xAd
        $ pip install -r requirements.txt

To invoke the worker script:
        $ python3 worker.py
This will invoke the script with timeout set to 60 seconds
        $ python worker.py -t 10
This will invoke the script with timeout set to 10 seconds.

## Expected Output

(streamproc) tharak src $ python3 worker.py -t 10
Worker 8: Failed to process stream. Exception: StreamError, ('',)
Worker[7]: [Elapsed]: 799.85ms [byte\_count]: 47000 [status]: SUCCESS
Worker[3]: [Elapsed]: 781.92ms [byte\_count]: 50000 [status]: SUCCESS
Worker[9]: [Elapsed]: 722.40ms [byte\_count]: 35000 [status]: SUCCESS
Worker[4]: [Elapsed]: 720.42ms [byte\_count]: 42000 [status]: SUCCESS
Worker[5]: [Elapsed]: 715.36ms [byte\_count]: 39000 [status]: SUCCESS
Worker[0]: [Elapsed]: 714.97ms [byte\_count]: 44000 [status]: SUCCESS
Worker[6]: [Elapsed]: 621.19ms [byte\_count]: 32000 [status]: SUCCESS
Worker[8]: [Elapsed]: 0.00ms [byte\_count]: 0 [status]: FAILURE
Worker[1]: [Elapsed]: 0.00ms [byte\_count]: 0 [status]:TIMEOUT
Worker[2]: [Elapsed]: 0.00ms [byte\_count]: 0 [status]:TIMEOUT
AVERAGE: Successful: 7 [Elapsed]: 725.16 [byte\_count]: 41285.71

You will see some streams that are TIMED OUT and some that report FAILURE. This is normal operation. The streams are simulated such that there is a 10% chance that the streams report a timeout and a 20% 
chance that they report FAILURE.


## Problem Statement:

Program spawns 10 workers (threads, processes, actors, whatever), where each worker simultaneously searches a stream of random (or pseudo-random) data for the string 'xAd', then informs the parent of the following data fields via some form of inter-process communication or shared data structure:
* elapsed time
* count of bytes read
* status

The parent collects the results of each worker (confined to a timeout, explained below) and writes a report to stdout for each worker sorted in descending order by [elapsed]:
[elapsed] [byte_cnt] [status]

Where [elapsed] is the elapsed time for that worker in ms, [byte\_cnt] is the number of random bytes read to find the target string and [status] should be one of {SUCCESS, TIMEOUT, FAILURE}. FAILURE should be reported for any error/exception of the worker and the specific error messages should go to stderr. TIMEOUT is reported if that worker exceeds a given time limit, where the program should support a command-line option for the timeout value that defaults to 60s. If the status is not SUCCESS, the [elapsed] and [byte\_cnt] fields will be empty.

The parent should always write a record for each worker and the total elapsed time of the program should not exceed the timeout limit. If a timeout occurs for at least one worker, only those workers that could not complete in time should report TIMEOUT, other workers may have completed in time and should report SUCCESS. Note that the source of random bytes must be a stream such that a worker will continue indefinitely until the target string is found, or a timeout or exception occurs. A final line of output will show the average time spent per byte read in units of your choice where failed/timeout workers will not report stats. 11 lines of output total to stdout.

## Implementation

### worker.py
The workers are derived from multiprocessing.Process. The only addition being the queue to pass information about the results to the parent process. We spawn the worker processes, check if the processes take longer than TIMEOUT PERIOD to process. If they do take longer than the TIMEOUT period, it is assumed that they have timed out. If the timeout argument passed to the program is too short (eg. 2 seconds),
streams that were programmed to be successful may also timeout. Once the process have completed the tasks or timed out we collect the results in the pretty\_log tuple. This is simply so we can print the results in the descending order of elapsed time. 

### streamer.py
The streamer module simulates the fake streams that the workers will search for the presence of the header "xAd". The interface for the streamer is get\_next() which will return the next ouput byte in the stream. Whether the stream will contain the header (SUCCESS), will fail with and exception (FAILURE) or will not contain the header (TIMEOUT) is controlled by the "outcome" variable. The "outcome" variable is programmed such that 20% of the streams fail, 10% timeout and the rest succeed to be able to test all possible scenarios involving streams.


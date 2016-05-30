# StreamProcessor

Program spawns 10 workers (threads, processes, actors, whatever), where each worker simultaneously searches a stream of random (or pseudo-random) data for the string 'xAd', then informs the parent of the following data fields via some form of inter-process communication or shared data structure:
* elapsed time
* count of bytes read
* status

The parent collects the results of each worker (confined to a timeout, explained below) and writes a report to stdout for each worker sorted in descending order by [elapsed]:
[elapsed] [byte_cnt] [status]

Where [elapsed] is the elapsed time for that worker in ms, [byte\_cnt] is the number of random bytes read to find the target string and [status] should be one of {SUCCESS, TIMEOUT, FAILURE}. FAILURE should be reported for any error/exception of the worker and the specific error messages should go to stderr. TIMEOUT is reported if that worker exceeds a given time limit, where the program should support a command-line option for the timeout value that defaults to 60s. If the status is not SUCCESS, the [elapsed] and [byte\_cnt] fields will be empty.

The parent should always write a record for each worker and the total elapsed time of the program should not exceed the timeout limit. If a timeout occurs for at least one worker, only those workers that could not complete in time should report TIMEOUT, other workers may have completed in time and should report SUCCESS. Note that the source of random bytes must be a stream such that a worker will continue indefinitely until the target string is found, or a timeout or exception occurs. A final line of output will show the average time spent per byte read in units of your choice where failed/timeout workers will not report stats. 11 lines of output total to stdout.

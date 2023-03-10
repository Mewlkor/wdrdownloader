import requests, datetime, time, os, sys, logging
import threading, multiprocessing
import argparse

stop_queue = multiprocessing.Queue()
arguement_parser = argparse.ArgumentParser()
arguement_parser.add_argument('--stream', '-s', nargs='?', const='WDR4', default='WDR4', help='The stream to download: 1Live, WDR2, WDR3, WDR4, WDR5')
arguement_parser.add_argument('--duration', '-d', nargs='?', const=1, default=1 ,help='The duration of the recording in minutes')
arguement_parser.add_argument('--filename', '-f', nargs='?', const='download', default='download' ,help='The filename of the recording')

wdr_streams = {'1Live': "https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3",
                'WDR2': "https://wdr-wdr2-ostwestfalenlippe.icecastssl.wdr.de/wdr/wdr2/ostwestfalenlippe/mp3/128/stream.mp3",
                'WDR3': "https://wdr-wdr3-live.icecastssl.wdr.de/wdr/wdr3/live/mp3/128/stream.mp3",
                'WDR4': "https://wdr-wdr4-live.icecastssl.wdr.de/wdr/wdr4/live/mp3/128/stream.mp3",
                'WDR5': "https://wdr-wdr5-live.icecastssl.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3"}


def download(stream_url , filename):
    stream_request = requests.get(stream_url, stream=True)
    with open(f'{filename}_{datetime.date.today()}.mp3', 'wb', 0) as f:
        try:
            for block in stream_request.iter_content(1024): # Write 1024 bytes at a time
                f.write(block)                              # Write to file
                f.flush()                                   # Flush to disk
                os.fsync(f)                                 # Force os to write to disk
                if(stop_queue.qsize() == 1):                # Check if stop_queue is not empty, if so, raise KeyboardInterrupt to stop download. Check after every block is written to file
                    raise KeyboardInterrupt
               
                
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    args = arguement_parser.parse_args()
    t1 = threading.Thread(target=download, args=(wdr_streams[args.stream], args.filename))
    logging.info('Starting download')
    t1.start()
    wait_time = int (args.duration)*60                      # Convert minutes to seconds
    time.sleep(wait_time)                                   # Wait for the specified amount of time
    logging.info('Stopping download')
    stop_queue.put(1)                                       # Put something in the queue to stop the download
    t1.join()
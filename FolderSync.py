import os, shutil, filecmp, time, logging, schedule, argparse



# Setup argument parser
parser = argparse.ArgumentParser(description='Sync directories')

# Add arguments
parser.add_argument('-s', '--src', type=str, help='Source directory path')
parser.add_argument('-d', '--dst', type=str, help='Destination directory path')
parser.add_argument('-l', '--log', type=str, help='Log file path')
parser.add_argument('-t', '--time', type=int, help='Time in seconds')
args = parser.parse_args()

# Check if arguments are empty
if args.src is None:
    print('Source directory is empty')
    exit()
if args.dst is None:
    print('Destination directory is empty')
    exit()
if args.log is None:
    print('Log file is empty')
    exit()
if args.time is None:
    print('Time is empty')
    exit()


# Source and destination paths
src = args.src
dst = args.dst

# Setup logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s', 
                                  datefmt='%d/%m/%Y %H:%M:%S')

# File to log to
logFile = args.log

# Setup File handler
file_handler = logging.FileHandler(logFile)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Setup Stream Handler (i.e. console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)

# Get our logger
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

# Add both Handlers
app_log.addHandler(file_handler)
app_log.addHandler(stream_handler)


# Function to sync directories
def SyncFolders(src, dst):
    # Get the list of files and directories i the source directory.
    source = os.listdir(src)
    # Get the list of files and directories in the destination directory.
    destination = os.listdir(dst)
    # Iterate over the directories in the source directory.
    for item in source:
        # Get the full path of the source directory.
        source_path = os.path.join(src, item)
        # Get the full path of the directory in the destination directory.
        destination_path = os.path.join(dst, item)
        # Check if item is a directory.
        if os.path.isdir(source_path):
                # Check if the directory exists in the destination directory.
                if os.path.exists(destination_path):
                    # If the directory exists, call the function once more.
                    SyncFolders(source_path, destination_path)
                else:
                    # If the directory does not exist, create it.
                    shutil.copytree(source_path, destination_path)
                    app_log.info('Directory %s created.' % destination_path)
        # Check if item is a file.
        elif os.path.isfile(source_path):
            # Check if the file exists in the destination directory.
            if os.path.exists(destination_path):
                # If the file exists, check if the file is the same.
                if filecmp.cmp(source_path, destination_path):
                    # If the file is the same, continue.
                    continue
                # If the file is not the same, overwrite the file.
                else:
                    shutil.copy2(source_path, destination_path)
                    app_log.info('File %s overwritten.' % destination_path)
            # If the file does not exist, copy the file.
            else:
                shutil.copy2(source_path, destination_path)
                app_log.info('File %s copied.' % destination_path)
    # Iterate over the directories in the destination directory.        
    for item in destination:
        # Check if item is not in the source directory.
        if item not in source:
            # Check if item is a directory.
            if os.path.isdir(os.path.join(dst, item)):
                # If item is a directory, remove the directory.
                shutil.rmtree(os.path.join(dst, item))
                app_log.info('Directory %s removed.' % os.path.join(dst, item))
            # Check if item is a file.    
            elif os.path.isfile(os.path.join(dst, item)):
                # If item is a file, remove the file.
                os.remove(os.path.join(dst, item))
                app_log.info('File %s removed.' % os.path.join(dst, item))


# Call function to sync directories every args.time seconds
schedule.every(args.time).seconds.do(SyncFolders, src, dst)

# Loop to run the schedule
while 1:
    schedule.run_pending()
    time.sleep(1)

import socket
import random
import time
import csv
import datetime
import argparse
from colorama import Back, Fore, Style

host = '192.168.0.37'
port = 8888
# Define the color and trajectory mappings
color_map = {1: "Green", 2: "Green", 3: "Red", 4: "Red"}
trajectory_map = {1: True, 2: False, 3: True, 4: False}
 
def custom_print(sequence):
    #print("Generated sequence for experiment: ")
    # Print the color and trajectory based on the number
    
    for num in sequence:
        color = color_map[num]
        trajectory = trajectory_map[num]

        if color == "Green":
            print(Back.GREEN + Fore.WHITE + str(trajectory) + Style.RESET_ALL)
        else:
            print(Back.RED + Fore.WHITE + str(trajectory) + Style.RESET_ALL)

def rand_seq_gen(num_block = 3, mistake = True):
    # Step 1: Create the sequence
    if mistake == True:
        sequence = [1, 2, 3, 4] * num_block  # Repeat "1 2 3 4" three times
    else:
        sequence = [1, 3] * num_block

    #print(sequence)
    # Step 2: Shuffle the sequence
    random.shuffle(sequence)

    # Print the shuffled sequence
    #custom_print(sequence)
   
    # Return the generated sequence
    return sequence

def block_indicate():
    while True:
        user_input = input("Please indicate block nums integer: ")
        try:
            block = int(user_input)
            if block >= 0:
                print("You will have ", block , "actions in the sequence")
                break
            else:
                print("Invalid input. Please enter a positive number.")
                break
        except ValueError:
            print("Invalid input. Please enter a real number.")

    return block

def mistake_indicate():
    while True:
        user_input = input("Enter 'True' or 'False' to enable Mistakes: ")
        if user_input.lower() in ['true', '1', 't', 'y', 'yes']:
            mistake = True
            break
        elif user_input.lower() in ['false', '0', 'f', 'n', 'no']:
            mistake = False
            break
        else:
            raise ValueError("Invalid input, please enter 'True' or 'False'.")
    return mistake

def gen_seq(block=3, mistake=True, sub_block=False):
    seq = rand_seq_gen(block, mistake)
    if sub_block:
        seq += rand_seq_gen(block, mistake)
    #seq = [3, 1, 3, 1, 3, 3, 1, 1, 1, 1, 3, 3, 3, 1, 1, 3]
    #print(seq)
    len_trial = len(seq) 
    print("Bottom sequence: \u2193")
    custom_print(seq[2*block : 4*block+1])

    print("Top sequence: \u2191")
    custom_print(seq[0 : 2*block])
   
    log = []
    seq_log =[]
    bits_list = []
    for num in seq:
        color = color_map[num]
        trajectoryTF = trajectory_map[num]
        log.append(color)

        if color == "Green":
            bits_list.append('z' if trajectoryTF else 'a')
            log.append('direct'if trajectoryTF else 'indirect')
        else:
            bits_list.append('a' if trajectoryTF else 'z')
            log.append('indirect'if trajectoryTF else 'direct')

        log.append(trajectoryTF)
        seq_log.append(log)
        log = []

    bits = ','.join(bits_list)
    #print("seq_log", seq_log)
    return bits, len_trial, seq_log
    
def task_time():
    while True:
        user_input = input("Please indicate your total time in seconds: ")
        try:
            wait_num = float(user_input)
            if wait_num >= 0:
                print("You will have ", wait_num, "second to try the tasks")
                break
            else:
                print("Invalid input. Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a real number.")

    return wait_num

def parse_arguments(*args, **kwargs):
    parser = argparse.ArgumentParser(description='TCP Server for Nova5 to run')
    parser.add_argument('--block', type=int, help='Block number')
    parser.add_argument('--mistake', action='store_true', help='Mistake flag (default: False)')
    parser.add_argument('--no-mistake', action='store_false', dest='mistake', help='Mistake flag (default: False)')
    parser.add_argument('--task_time', type=float, help='Task time in seconds')
    
    # Allow the parser to take args and kwargs
    return parser.parse_args(*args, **kwargs)

def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def log_start_time(filename):
    current_time = get_current_time()
    column_names = ["Trial no.", "Operation time", "Color", "Trajectory", "T/F"]
    #print(current_time, column_names)
    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Experiment block start time', current_time])
        csv_writer.writerow(column_names)

def process_and_save_data(received_data, seq_log):
    data_filename = f"data_{get_current_date()}.csv"
    log_start_time(data_filename) 

    # Assuming the data format is ['name', 'value', 'finished']
    for i in range(len(received_data)):
        name, value = received_data[i]
        color, traj, TF = seq_log[i]
        try:
            # Convert value to float and divide by 1000
            value = float(value) / 1000
        except ValueError:
            print(f"Invalid value received: {value}")
            return
        
        data_to_csv=[name,value,color,traj,TF]
        #print(data_to_csv)
        with open(data_filename, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(data_to_csv)


def main(*args, **kwargs):
    args = parse_arguments(*args, **kwargs)

    block = args.block if args.block is not None else block_indicate()
    mistake = args.mistake if args.mistake is not None else mistake_indicate()
    wait_time = args.task_time if args.task_time is not None else task_time()
    #print(block, mistake)
    
    received_data = []
    sub_block = not mistake
    bits, len_trial, seq_log = gen_seq(block, mistake, sub_block)
    data_send = str(len_trial) + "," + bits + "," + str(wait_time)

    input("When you are ready placed the cubes, press ENTER")
    start_t = time.time()
    try: 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        #client_socket.send(len_trial.encode('utf-8'))
        
        print(f"Connected to server: {host}:{port}")
        client_socket.send(data_send.encode('utf-8'))
    except Exception as e:
        print(f"An error occurred: {e}")
    
    data_str = []
    
    while True:
        data_recv = client_socket.recv(1024)
        if data_recv is not None:
            data_str.append(data_recv.decode('utf-8'))

        if data_recv.decode('utf-8') == "finished":
            print("Time used for task", data_str[0], "is", float(data_str[1])/1000, "second!")
            received_data.append(data_str[:-1])
            data_str = []

        if data_recv.decode('utf-8') == "ff":
            #print("received_data", received_data)
            print("Received 'finished' message, closing connection.")
            process_and_save_data(received_data, seq_log)
            break
    time_used = time.time() - start_t
    print("This block takes", time_used, "seconds!")
    client_socket.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])

import socket
import random
import time
import csv
import datetime
import os
import cv2
import threading
from tkinter import scrolledtext
import tkinter as tk

task_time = 4.0
button_params = [
    {'text': 'Baseline', 'num_block': 1, 'wait_time': task_time},
    {'text': 'Practice', 'num_block': 2, 'wait_time': task_time},
    {'text': 'Block 1', 'num_block': 3, 'wait_time': task_time},
    {'text': 'Block 2', 'num_block': 4, 'wait_time': task_time},
    {'text': 'Block 3', 'num_block': 5, 'wait_time': task_time},
]

host = '192.168.0.37'
port = 8888
# Define the color and trajectory mappings
color_map = {1: "Green", 2: "Green", 3: "Red", 4: "Red"}
trajectory_map = {1: True, 2: False, 3: True, 4: False}
# Global variable to store the clicked button's label
clicked_button_label = None

# Define a stop event for threading
stop_event = threading.Event()
app = tk.Tk()

# Global variable to store the clicked button's label
clicked_button_label = None

def video_recording():
    index, width, height = [0,1920,1080]
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec used to compress the frames
    filename = f'video_{get_current_time()}.avi'
    out = cv2.VideoWriter(filename, fourcc, 30.0, (width, height))  # Output file, codec, frames per second, and frame size

    # Initialize the camera
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    time_start = time.time()

    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return
    
    while time.time() - time_start < 300 and not stop_event.is_set():
        # record for 300 seconds
        # Capture frame-by-frame
        
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Our operations on the frame come here
        # Write the frame into the file 'output.avi'
        out.write(frame)

        # Display the resulting frame
        #cv2.imshow('frame', frame)
    
    elapsed_time = time.time() - time_start

    if elapsed_time < 100:
        print(f"Recording was too short ({elapsed_time:.2f} seconds). Deleting file: {filename}")
        os.remove(filename)
    else:
        print(f"Recording saved: {filename}")
    # When everything done, release the capture
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Video recording stopped and resources released.")

def custom_print(sequence, text_widget):
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, "left ")
    for num in sequence:
        color = color_map[num]
        trajectory = trajectory_map[num]
        if color == "Green":
            text_widget.insert(tk.END, str(trajectory) + " ", "green")
        else:
            text_widget.insert(tk.END, str(trajectory) + " ", "red")
    
    text_widget.insert(tk.END, " right\n")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only

def gen_seq(num_block):
    match num_block:
        case 1:
            sequence = [1,3]*2
            random.shuffle(sequence)
        case 2:
            sequence = [1,3]*2
            random.shuffle(sequence)
        case 3:
            seq_1 = [1,3]*4
            random.shuffle(seq_1)
            seq_2 = [1,3]*4
            random.shuffle(seq_2)
            sequence = seq_1 + seq_2
        case 4:
            seq_1 = [2,4]
            random.shuffle(seq_1)
            seq_2 = [1,3]+[1,2,3,4]
            random.shuffle(seq_2)
            seq_3 = [1,2,3,4]*2
            random.shuffle(seq_3)
            sequence = seq_1 + seq_2 + seq_3
        case 5:
            seq_1 = [1,3]*4
            random.shuffle(seq_1)
            seq_2 = [1,3]*4
            random.shuffle(seq_2)
            sequence = seq_1 + seq_2

    return sequence

def tcp_send_received(data, seq_log, text_widget):
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, "Starting actions for " + clicked_button_label +"!\n")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
    start_t = time.time()
    try: 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        #client_socket.send(len_trial.encode('utf-8'))
        
        print(f"Connected to server: {host}:{port}")
        client_socket.send(data.encode('utf-8'))

    except Exception as e:
        print(f"An error occurred: {e}")
        return

    data_str = []
    received_data = []
    while True:
        try: 
            data_recv = client_socket.recv(1024)
        except Exception as e:
            print(f"An error occurred: {e}")
            return
        
        if data_recv is not None:
            data_str.append(data_recv.decode('utf-8'))

        if data_recv.decode('utf-8') == "finished":
            print("Time used for task", data_str[0], "is", float(data_str[1])/1000, "second!")
            received_data.append(data_str[:-1])
            data_str = []

        if data_recv.decode('utf-8') == "ff":
            #print("received_data", received_data)
            print("Received 'finished' message, closing connection.")
            print(received_data)
            process_and_save_data(received_data, seq_log)
            break

    time_used = time.time() - start_t
    print("This block takes", time_used, "seconds!")
    client_socket.close()
    
    filename = f"data_{get_current_date()}.csv"
    with open(filename, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([f'Experiment {clicked_button_label} finished using {time_used} seconds'])

    message = f"{clicked_button_label} finished using {time_used} seconds!\n"
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, message)
    text_widget.see(tk.END)  # Scroll to the bottom
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only

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

    # Check if the file exists to avoid permission issues
    if not os.path.exists(data_filename):
        with open(data_filename, 'w', newline='') as csvfile:
            pass  # Just create the file

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
    
def seq_radom(num_block, wait_time, text_widget):
    seq = gen_seq(num_block)
    len_trial = len(seq)
    half_trial = int(len_trial/2)

    seq_up = seq[0 : half_trial]
    seq_up.reverse()
    seq_bottom = seq[half_trial : len_trial+1]
    seq_bottom.reverse()

    custom_print(seq_up, text_widget)
    custom_print(seq_bottom, text_widget)
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, "Please assemble the cubes based on this placement\n", "yellow")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
   
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

    data_send = str(len_trial) + "," + bits + "," + str(wait_time)

    return data_send, seq_log

def on_button_click(num_block, wait_time, text_widget, button_label, start_button):
    global clicked_button_label
    clicked_button_label = button_label
    
    stop_event.set()
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    #text_widget.delete(1.0, tk.END)  # Clear the widget
    text_widget.insert(tk.END, "\n")
    text_widget.insert(tk.END, "you have selected " + clicked_button_label + " to play!\n")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
    data_send, seq_log = seq_radom(num_block, wait_time, text_widget)
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, "Press start when you are ready!\n", "yellow")
    text_widget.see(tk.END)  # Scroll to the bottom
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
    
    def start_button_action():
        stop_event.clear()  # Reset stop event in case it was set
        if num_block > 2:
            # Set up and start the video recording thread
            video_thread = threading.Thread(target=video_recording, args=())
            video_thread.start()
        tcp_send_received(data_send, seq_log, text_widget)
        
        if video_thread.is_alive():
            stop_event.set()  # Ensure the video recording thread has finished
            video_thread.join()

    start_button.config(text=f"Start {button_label}", command=start_button_action)
    start_button.pack(pady=5)

def on_close():
    print("Stopping recording and closing application...")
    stop_event.set()  # Signal the recording thread to stop
    app.destroy()  # Close the tkinter window


def main():
    global start_button
    # Create the main window
    app.title("Cobot Malfunction Experiment GUI")
    
    # Set up the protocol for the window close button (X button)
    app.protocol("WM_DELETE_WINDOW", on_close)

    # Create a label to display messages
    label = tk.Label(app, text="Choose which block you want to run!")
    label.pack(pady=10)

    # Create a scrolled text widget for displaying output
    text_widget = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=60, height=20)
    text_widget.pack(pady=10)
    text_widget.tag_configure("green", foreground="white", background="green")
    text_widget.tag_configure("red", foreground="white", background="red")
    text_widget.tag_configure("yellow", foreground="black", background="yellow")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
    
    text_widget.config(state=tk.NORMAL)  # Make the widget editable
    text_widget.insert(tk.END, "Recording started!!!\n")
    text_widget.insert(tk.END, "Please select one block to begin with\n")
    text_widget.config(state=tk.DISABLED)  # Make the widget read-only
    # Create the start button but don't pack it yet
    start_button = tk.Button(app, text="")
    
    # Create and place buttons
    for params in button_params:
        button = tk.Button(app, text=params['text'], command=lambda p=params:on_button_click(p['num_block'], p['wait_time'], text_widget, p['text'], start_button))
        button.pack(pady=5)

    # Run the application
    app.mainloop()


if __name__ == "__main__":
    main()

# Nova5
Nova5 Development with TCP communication

To run the Dobot Nova5 robot with psycological experiments:

`--block` specifies `int` number of iterations in one block, trials will be **4** times of block number

`-- mistake` or `--no-mistake` specifies if mistakes exsit in the block

`--task_time` specifies the `float` time waiting at the home spot

```
python3 tcp_client.py --block 4 --mistake --task_time 5
```
OR using it with a simple gui

```
python3 cobot_malfunction.py
```
Go to the same location with the python scipt with a subfolder of `data`, you could find the csv data. Besides, the video is also stored under `video` subforlder

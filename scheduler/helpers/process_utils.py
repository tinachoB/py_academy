import os
import socket
import subprocess
from os import path
import psutil


class ProcessMgr:
    def __init__(self: "ProcessMgr", json_config_data) -> None:
        self.json_data = json_config_data
        self.pid = 0
        self.file_pid = 0

    def start(self: "ProcessMgr") -> None:
        if self._is_running():
            if self._read_pid_from_file():
                if str(self.pid) == str(self.file_pid):
                    print(f'{self.json_data["program_name"]} process is running...')
                else:
                    self._write_pid_to_file()
            else:
                self._write_pid_to_file()
        else:
            self._start_process()

    def write(self: "ProcessMgr") -> None:
        socket_name = self.json_data["socket_name"]
        if path.exists(socket_name):
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(socket_name)
                sock.send((self.json_data["message"]).encode('utf-8'))
            except Exception as error:
                print(f"Unable to connect to socket {socket_name}. Error {error}")
        else:
            print(f"Unable to find socket: {socket_name}")

    def stop(self: "ProcessMgr") -> None:
        if self._read_pid_from_file():
            if psutil.pid_exists(int(self.file_pid)):
                for process in psutil.process_iter():
                    try:
                        if str(process.pid) == str(self.file_pid):
                            process.terminate()
                            os.remove(self.json_data["pidfile_name"])
                            print(f"The {self.file_pid} has been stopped successfully")
                    except Exception as error:
                        print(f"Unable to terminate process. Error {error}")
            else:
                print(f"The process {self.file_pid} is not running")
                # Removing pid file
                os.remove(self.json_data["pidfile_name"])
        else:
            print("Unable to read PID file")

    #
    # Private functions section
    #

    def _start_process(self: "ProcessMgr"):
        program_name = self.json_data["program_name"]
        try:
            process = subprocess.Popen(program_name, shell=True, stdout=None, stderr=None)
            if self._is_running():
                self._write_pid_to_file()
            else:
                print(f"{program_name} process is not running")
        except Exception as error:
            print(f"Unable to start process {program_name}. Error {error}")

    def _is_running(self: "ProcessMgr"):
        program_name = self.json_data["program_name"]
        for process in psutil.process_iter():
            try:
                if process.name() == program_name:
                    # Process found! Save its pid
                    self.pid = process.pid
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
                print(f"Unable to get processes information. Error {error}")
                pass
        return False

    def _read_pid_from_file(self: "ProcessMgr"):
        ret = False
        try:
            with open(self.json_data["pidfile_name"], "r") as pid_file:
                self.file_pid = pid_file.readline()
                ret = True
        except IOError:
            print("Unable to open pid file")
        return ret

    def _write_pid_to_file(self: "ProcessMgr"):
        pid_file = self.json_data["pidfile_name"]
        if path.exists(pid_file):
            os.remove(pid_file)
        # Opening with write permission
        with open(pid_file, "w+") as file:
            pid = file.write(str(self.pid))
            print(f"The PID {self.pid} has been updated successfully")

##
# Main entry point
#
import sys
import threading
import multiprocessing
import time
import schedule
from helpers.json import json_utils
from helpers import process_utils


class TVScheduler:
    def __init__(self, json_task) -> None:
        # JSON content of the specific task passed as argument
        self.json_data = json_utils.validate(json_task)
        # Process manager instance in charge of all process related actions
        self.process_mgr = process_utils.ProcessMgr(self.json_data)
        # Event thread which represents the entire lifecycle of the application
        self.stop_evt = threading.Event()
        # Event thread which represents the entire lifecycle of the task being executed
        self.task_completion_evt = threading.Event()
        # Task timeout value
        self.TASK_TIMEOUT = 20

    def start(self) -> None:
        schedule.every().day.at(self.json_data["time"]).do(self._do_job, self.json_data["verb"])
        # Lets iterate until an external event occur (mainly a ctrl+c keyboard interruption)
        while not self.stop_evt.is_set():
            schedule.run_pending()
            time.sleep(1)

    def stop(self) -> None:
        self.stop_evt.set()

    #
    # Private functions section
    #

    def _do_job(self, action: str) -> None:
        self.task_completion_evt.clear()
        process = {}
        if action == "start":
            process = multiprocessing.Process(target=self._start_process())
        elif action == "write":
            process = multiprocessing.Process(target=self._write_process())
        else:
            # stop action
            process = multiprocessing.Process(target=self._stop_process())

        process.name = action
        process.start()
        process.join(self.TASK_TIMEOUT)

        if process.is_alive():
            print(f"TIMEOUT has reached.. terminating process: {process.name}")
            try:
                process.terminate()
            except Exception as error:
                print(f"Unable to terminate running {process.name} process. Error {error}")
                process.kill()

        self.task_completion_evt.set()

    def _start_process(self) -> None:
        self.process_mgr.start()

    def _write_process(self) -> None:
        self.process_mgr.write()

    def _stop_process(self) -> None:
        self.process_mgr.stop()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        tv_scheduler = TVScheduler(sys.argv[1])
        try:
            tv_scheduler.start()
        except KeyboardInterrupt:
            tv_scheduler.stop()
            sys.exit()
    else:
        print("Invalid application usage. Correct usage: python3 TVScheduler.py <json_task>.py")

from os import listdir
from os.path import join
from shutil import rmtree

from s3_operations import S3_Operation

from utils.logger import App_Logger
from utils.read_params import read_params


class Main_Utils:
    def __init__(self):
        self.class_name = self.__class__.__name__

        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

        self.config = read_params()

        self.bucket = self.config["s3_bucket"]

        self.log_dir = self.config["log_dir"]

        self.log_file = self.config["log"]["upload"]

        self.data_dir = self.config["data_dir"]

    def upload_logs(self):
        method_name = self.upload_logs.__name__

        self.log_writer.start_log("start", self.class_name, method_name, self.log_file)

        try:
            lst = listdir(self.log_dir)

            self.log_writer.log(
                f"Got list of logs from {self.log_dir} folder", self.log_file
            )

            for f in lst:
                local_f = join(self.log_dir, f)

                dest_f = self.log_dir + "/" + f

                self.s3.upload_file(local_f, dest_f, self.bucket["logs"], self.log_file)

            self.log_writer.log(
                f"Uploaded logs to {self.bucket['logs']}", self.log_file
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.log_file
            )

            rmtree(self.log_dir)

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.log_file
            )

    def get_pred_fname(self, key, fname, log_file):
        method_name = self.get_pred_fname.__name__

        self.log_writer.start_log("start", self.class_name, method_name, log_file)

        try:
            pred_fname = self.data_dir[key] + "/" + fname

            self.log_writer.log(f"Got the pred file name for {key}", log_file)

            self.log_writer.start_log("exit", self.class_name, method_name, log_file)

            return pred_fname

        except Exception as e:
            self.log_writer.exception_log(e, self.class_name, method_name, log_file)
from os import listdir
from os.path import join
from shutil import rmtree

from s3_operations import S3_Operation

from utils.logger import App_Logger
from utils.read_params import read_params


class Main_Utils:
    """
    Description :   This class is used for main utility functions required in core functions of the service
    Version     :   1.2
    
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

        self.config = read_params()

        self.files = self.config["files"]

        self.bucket = self.config["s3_bucket"]

        self.class_name = self.__class__.__name__

        self.log_file = self.config["log"]["upload"]

        self.log_dir = self.config["log_dir"]

    def upload_logs(self):
        """
        Method Name :   upload_logs
        Description :   This method uploads the logs to s3 bucket
        
        Output      :   The logs are uploaded to s3 bucket
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """

        method_name = self.upload_logs.__name__

        self.log_writer.start_log("start", self.class_name, method_name, self.log_file)

        try:
            lst = listdir(self.log_dir)

            self.log_writer.log("Got list of logs from app_logs folder", self.log_file)

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

    def upload_data_to_feature_store(self, data, key, log_file):
        """
        Method Name :   upload_data_to_feature_store
        Description :   This method uploads the data the feature store bucket based on key 
        
        Output      :   The data is uploaded to feature store bucket
        On Failure  :   Write an exception log and then raise an exception
        
        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.upload_data_to_feature_store.__name__

        self.log_writer.start_log("start", self.class_name, method_name, log_file)

        try:
            self.s3.upload_df_as_csv(
                data,
                self.files[key],
                self.files[key],
                self.bucket["feature_store"],
                log_file,
            )

            self.log_writer.log(f"Uploaded {key} to feature store bucket", log_file)

            self.log_writer.start_log("exit", self.class_name, method_name, log_file)

        except Exception as e:
            self.log_writer.exception_log(e, self.class_name, method_name, log_file)

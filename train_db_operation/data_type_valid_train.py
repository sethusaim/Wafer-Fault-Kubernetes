from mongo_db_operations import MongoDB_Operation
from utils.logger import App_Logger
from utils.read_params import read_params
from s3_operations import S3_Operation


class DB_Operation_Train:
    """
    Description :    This class shall be used for handling all the db operations
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.class_name = self.__class__.__name__

        self.bucket = self.bucket["s3_bucket"]

        self.files = self.config["files"]

        self.data_dir = self.config["data_dir"]

        self.train_db_insert_log = self.config["log"]["db_insert"]

        self.train_export_csv_log = self.config["log"]["export_csv"]

        self.s3 = S3_Operation()

        self.mongo = MongoDB_Operation()

        self.log_writer = App_Logger()

    def insert_good_data_as_record(
        self, good_data_db_name: str, good_data_collection_name: str
    ):
        """
        Method Name :   insert_good_data_as_record
        Description :   This method inserts the good data in MongoDB as collection

        Output      :   A MongoDB collection is created with good data present in it
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.insert_good_data_as_record.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.train_db_insert_log,
        )

        try:
            lst = self.s3.read_csv_from_folder(
                self.data_dir["train_good"],
                self.bucket["train_data"],
                self.train_db_insert_log,
            )

            for idx, f in enumerate(lst):
                df = f[idx][0]

                file = f[idx][1]

                if file.endswith(".csv"):
                    self.mongo.insert_dataframe_as_record(
                        df,
                        good_data_db_name,
                        good_data_collection_name,
                        self.train_db_insert_log,
                    )

                else:
                    pass

                self.log_writer.log(
                    "Inserted dataframe as collection record in mongodb",
                    self.train_db_insert_log,
                )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.train_db_insert_log,
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.train_db_insert_log,
            )

    def export_collection_to_csv(
        self, good_data_db_name: str, good_data_collection_name: str
    ):
        """
        Method Name :   export_collection_to_csv
        Description :   This method inserts the good data in MongoDB as collection

        Output      :   A csv file stored in input files bucket, containing good data which was stored in MongoDB
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.export_collection_to_csv.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.train_export_csv_log,
        )

        try:
            df = self.mongo.get_collection_as_dataframe(
                good_data_db_name, good_data_collection_name, self.train_export_csv_log
            )

            self.s3.upload_df_as_csv(
                df,
                self.files["train_export"],
                self.files["train_export"],
                self.bucket["input_files"],
                self.train_export_csv_log,
            )

            self.log_writer.log(
                "Exported dataframe to csv file", self.train_export_csv_log
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.train_export_csv_log,
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.train_export_csv_log,
            )

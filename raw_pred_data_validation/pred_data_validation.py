from re import match, split

from s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.main_utils import Main_Utils
from utils.read_params import read_params


class Raw_Pred_Data_Validation:
    """
    Description :   This method is used for validating the raw prediction data
    Written by  :   iNeuron Intelligence
    
    Version     :   1.2
    Revisions   :   Moved to setup to cloud 
    """

    def __init__(self):
        self.config = read_params()

        self.class_name = self.__class__.__name__

        self.log_writer = App_Logger()

        self.utils = Main_Utils()

        self.s3 = S3_Operation()

        self.bucket = self.config["s3_bucket"]

        self.data_dir = self.config["data_dir"]

        self.files = self.config["files"]

        self.pred_log = self.config["log"]

    def values_from_schema(self):
        """
        Method Name :   values_from_schema
        Description :   This method gets schema values from the schema_prediction.json file

        Output      :   Schema values are extracted from the schema_prediction.json file
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.values_from_schema.__name__

        try:
            self.log_writer.start_log(
                "start",
                self.class_name,
                method_name,
                self.pred_log["values_from_schema"],
            )

            dic = self.s3.read_json(
                self.files["pred_schema"],
                self.bucket["io_files"],
                self.pred_log["values_from_schema"],
            )

            LengthOfDateStampInFile = dic["LengthOfDateStampInFile"]

            LengthOfTimeStampInFile = dic["LengthOfTimeStampInFile"]

            column_names = dic["ColName"]

            NumberofColumns = dic["NumberofColumns"]

            message = (
                "LengthOfDateStampInFile:: %s" % LengthOfDateStampInFile
                + "\t"
                + "LengthOfTimeStampInFile:: %s" % LengthOfTimeStampInFile
                + "\t "
                + "NumberofColumns:: %s" % NumberofColumns
                + "\n"
            )

            self.log_writer.log(message, self.pred_log["values_from_schema"])

            self.log_writer.start_log(
                "exit",
                self.class_name,
                method_name,
                self.pred_log["values_from_schema"],
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_log["values_from_schema"],
            )

        return (
            LengthOfDateStampInFile,
            LengthOfTimeStampInFile,
            column_names,
            NumberofColumns,
        )

    def get_regex_pattern(self):
        """
        Method Name :   get_regex_pattern
        Description :   This method gets regex pattern from input files s3 bucket

        Output      :   A regex pattern is extracted
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.get_regex_pattern.__name__

        try:
            self.log_writer.start_log(
                "start", self.class_name, method_name, self.pred_log["general"],
            )

            regex = self.s3.read_text(
                self.files["regex"], self.bucket["io_files"], self.pred_log["general"],
            )

            self.log_writer.log(f"Got {regex} pattern", self.pred_log["general"])

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.pred_log["general"],
            )

            return regex

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_log["general"],
            )

    def create_dirs_for_good_bad_data(self, log_file):
        """
        Method Name :   create_dirs_for_good_bad_data
        Description :   This method creates folders for good and bad data in s3 bucket

        Output      :   Good and bad folders are created in s3 bucket
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.create_dirs_for_good_bad_data.__name__

        self.log_writer.start_log("start", self.class_name, method_name, log_file)

        try:
            self.s3.create_folder(
                self.data_dir["pred_good"], self.bucket["pred_data"], log_file
            )

            self.s3.create_folder(
                self.data_dir["pred_bad"], self.bucket["pred_data"], log_file
            )

            self.log_writer.log(
                f"Created folders for good and bad data in {self.bucket['pred_data']}",
                log_file,
            )

            self.log_writer.start_log("exit", self.class_name, method_name, log_file)

        except Exception as e:
            self.log_writer.exception_log(e, self.class_name, method_name, log_file)

    def validate_raw_fname(
        self, regex, LengthOfDateStampInFile, LengthOfTimeStampInFile
    ):
        """
        Method Name :   validate_raw_fname
        Description :   This method validates the raw file name based on regex pattern and schema values

        Output      :   Raw file names are validated, good file names are stored in good data folder and rest is stored in bad data
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.validate_raw_fname.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.pred_log["name_validation"],
        )

        try:
            self.create_dirs_for_good_bad_data(self.pred_log["name_validation"])

            onlyfiles = self.s3.get_files_from_folder(
                self.data_dir["raw_pred_batch"],
                self.bucket["raw_pred_data"],
                self.pred_log["name_validation"],
            )

            pred_batch_files = [f.split("/")[1] for f in onlyfiles]

            self.log_writer.log(
                "Got prediction files with absolute file name",
                self.pred_log["name_validation"],
            )

            for fname in pred_batch_files:
                raw_data_pred_fname = self.utils.get_pred_fname(
                    "raw_pred_batch", fname, self.pred_log["name_validation"]
                )

                good_data_pred_fname = self.utils.get_pred_fname(
                    "pred_good", fname, self.pred_log["name_validation"]
                )

                bad_data_pred_fname = self.utils.get_pred_fname(
                    "pred_bad", fname, self.pred_log["name_validation"]
                )

                self.log_writer.log(
                    "Created raw,good and bad data file name",
                    self.pred_log["name_validation"],
                )

                if match(regex, fname):
                    splitAtDot = split(".csv", fname)

                    splitAtDot = split("_", splitAtDot[0])

                    if len(splitAtDot[1]) == LengthOfDateStampInFile:
                        if len(splitAtDot[2]) == LengthOfTimeStampInFile:
                            self.s3.copy_data(
                                raw_data_pred_fname,
                                self.bucket["raw_pred_data"],
                                good_data_pred_fname,
                                self.bucket["pred_data"],
                                self.pred_log["name_validation"],
                            )

                        else:
                            self.s3.copy_data(
                                raw_data_pred_fname,
                                self.bucket["raw_pred_data"],
                                bad_data_pred_fname,
                                self.bucket["pred_data"],
                                self.pred_log["name_validation"],
                            )

                    else:
                        self.s3.copy_data(
                            raw_data_pred_fname,
                            self.bucket["raw_pred_data"],
                            bad_data_pred_fname,
                            self.bucket["pred_data"],
                            self.pred_log["name_validation"],
                        )
                else:
                    self.s3.copy_data(
                        raw_data_pred_fname,
                        self.bucket["raw_pred_data"],
                        bad_data_pred_fname,
                        self.bucket["pred_data"],
                        self.pred_log["name_validation"],
                    )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.pred_log["name_validation"],
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_log["name_validation"],
            )

    def validate_col_length(self, NumberofColumns):
        """
        Method Name :   validate_col_length
        Description :   This method validates the column length based on number of columns as mentioned in schema values

        Output      :   The files' columns length are validated and good data is stored in good data folder and rest is stored in bad data folder
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.validate_col_length.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.pred_log["col_validation"],
        )

        try:
            lst = self.s3.read_csv_from_folder(
                self.data_dir["pred_good"],
                self.bucket["pred_data"],
                self.pred_log["col_validation"],
            )

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                if df.shape[1] == NumberofColumns:
                    pass

                else:
                    dest_f = self.data_dir["pred_bad"] + "/" + abs_f

                    self.s3.move_data(
                        file,
                        self.bucket["pred_data"],
                        dest_f,
                        self.bucket["pred_data"],
                        self.pred_log["col_validation"],
                    )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.pred_log["col_validation"],
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_log["col_validation"],
            )

    def validate_missing_values_in_col(self):
        """
        Method Name :   validate_missing_values_in_col
        Description :   This method validates the missing values in columns

        Output      :   Missing columns are validated, and good data is stored in good data folder and rest is to stored in bad data folder
        On Failure  :   Write an exception log and then raise an exception

        Version     :   1.2
        Revisions   :   moved setup to cloud
        """
        method_name = self.validate_missing_values_in_col.__name__

        self.log_writer.start_log(
            "start",
            self.class_name,
            method_name,
            self.pred_log["missing_values_in_col"],
        )

        try:
            lst = self.s3.read_csv_from_folder(
                self.data_dir["pred_good"],
                self.bucket["pred_data"],
                self.pred_log["missing_values_in_col"],
            )

            for _, f in enumerate(lst):
                df = f[0]

                file = f[1]

                abs_f = f[2]

                count = 0

                for cols in df:
                    if (len(df[cols]) - df[cols].count()) == len(df[cols]):
                        count += 1

                        dest_f = self.data_dir["pred_bad"] + "/" + abs_f

                        self.s3.move_data(
                            file,
                            self.bucket["pred_data"],
                            dest_f,
                            self.bucket["pred_data"],
                            self.pred_log["missing_values_in_col"],
                        )

                        break

                if count == 0:
                    dest_f = self.data_dir["pred_good"] + "/" + abs_f

                    self.s3.upload_df_as_csv(
                        df,
                        abs_f,
                        dest_f,
                        self.bucket["pred_data"],
                        self.pred_log["missing_values_in_col"],
                    )

                else:
                    pass

                self.log_writer.start_log(
                    "exit",
                    self.class_name,
                    method_name,
                    self.pred_log["missing_values_in_col"],
                )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_log["missing_values_in_col"],
            )
from data_type_valid_pred import DB_Operation_Pred
from utils.logger import App_Logger
from utils.main_utils import Main_Utils
from utils.read_params import read_params


class Run:
    def __init__(self):
        self.config = read_params()

        self.class_name = self.__class__.__name__

        self.pred_main_log = self.config["log"]["db_main"]

        self.mongo_config = self.config["mongodb"]

        self.log_writer = App_Logger()

        self.db_operation = DB_Operation_Pred()

    def pred_data_type_valid(self):
        method_name = self.pred_data_type_valid.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.pred_main_log,
        )

        try:
            self.log_writer.log(
                "Data type validation operation started !!", self.pred_main_log
            )

            self.db_operation.insert_good_data_as_record(
                self.mongo_config["db_name"], self.mongo_config["collection_name"]
            )

            self.db_operation.export_collection_to_csv(
                self.mongo_config["db_name"], self.mongo_config["collection_name"]
            )

            self.log_writer.log(
                "Data type validation Operation completed !!", self.pred_main_log
            )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.pred_main_log,
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.pred_main_log,
            )


if __name__ == "__main__":
    try:
        run = Run()

        run.pred_data_type_valid()

    except Exception as e:
        raise e

    finally:
        utils = Main_Utils()

        utils.upload_logs()
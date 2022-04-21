from s3_operations import S3_Operation
from utils.logger import App_Logger
from utils.main_utils import Main_Utils
from utils.model_utils import Model_Utils
from utils.read_params import read_params


class Run:
    def __init__(self):
        self.class_name = self.__class__.__name__

        self.config = read_params()

        self.model_utils = Model_Utils()

        self.utils = Main_Utils()

        self.s3 = S3_Operation()

        self.log_writer = App_Logger()

        self.model_train_log = self.config["log"]["model_train"]

        self.bucket = self.config["s3_bucket"]

        self.model_dir = self.config["model_dir"]

        self.save_format = self.config["model_save_format"]

        self.files = self.config["files"]

    def training_model(self):
        method_name = self.training_model.__name__

        self.log_writer.start_log(
            "start", self.class_name, method_name, self.model_train_log
        )

        try:
            feat_fnames = self.s3.get_files_from_folder(
                self.files["features"],
                self.bucket["feature_store"],
                self.model_train_log,
            )

            lst_clusters = len(feat_fnames)

            self.log_writer.log(
                f"Found the number of cluster to be {lst_clusters}",
                self.model_train_log,
            )

            for i in range(lst_clusters):
                feat_name = self.utils.get_cluster_fname(
                    "features", i, self.model_train_log
                )

                label_name = self.utils.get_cluster_fname(
                    "labels", i, self.model_train_log
                )

                self.log_writer.log(
                    "Got the cluster features and cluster label file names",
                    self.model_train_log,
                )

                cluster_feat = self.s3.read_csv(
                    feat_name, self.bucket["feature_store"], self.model_train_log
                )

                cluster_label = self.s3.read_csv(
                    label_name, self.bucket["feature_store"], self.model_train_log
                )

                self.log_writer.log(
                    f"Got cluster features and cluster labels dataframe from {self.bucket['feature_store']} bucket",
                    self.model_train_log,
                )

                self.model_utils.train_models(
                    cluster_feat, cluster_label, self.model_train_log
                )

            self.log_writer.start_log(
                "exit", self.class_name, method_name, self.model_train_log
            )

        except Exception as e:
            self.log_writer.exception_log(
                e, self.class_name, method_name, self.model_train_log
            )


if __name__ == "__main__":
    try:
        run = Run()

        run.training_model()

    except Exception as e:
        raise e

    finally:
        utils = Main_Utils()

        utils.upload_logs()

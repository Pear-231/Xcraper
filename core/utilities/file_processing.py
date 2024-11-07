import pandas
from pathlib import Path

class FileProcessing:
    @staticmethod
    def import_from_csv(file_path):
        if Path(file_path).suffix == ".csv":
            print(f"Importing {file_path}")
            data_frame = pandas.read_csv(file_path).fillna("")
            posts_data = data_frame.to_dict(orient="records")
            return posts_data

    @staticmethod
    def export_to_csv(file_path, csv_output_data):
        if Path(file_path).suffix == ".csv":
            print(f"Exporting {file_path}")
            data_frame = pandas.DataFrame(csv_output_data)
            data_frame.to_csv(file_path, index=False, encoding="utf-8-sig")
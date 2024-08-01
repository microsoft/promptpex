import pandas as pd
import pathlib, csv, io

class Utils:
    def join_csv_files(self, file1 : pathlib.Path, file2 : pathlib.Path, on : str, output : pathlib.Path):
        file1 = file1.read_text()
        file2 = file2.read_text()

        df1 = pd.read_csv(io.StringIO(file1), dtype=str)
        df2 = pd.read_csv(io.StringIO(file2), dtype=str)
        df = pd.merge(df1, df2, on=on)
        if not output.exists():
            df.to_csv(output, index=False)
            return
        df.to_csv(output, index=False, mode='a', header=False)

Utils = Utils()
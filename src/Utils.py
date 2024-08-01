import pandas as pd
import pathlib, csv

class Utils:
    def join_csv_files(self, file1 : pathlib.Path, file2 : pathlib.Path, on : str, output : pathlib.Path):
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        df = pd.merge(df1, df2, on=on)
        if not output.exists():
            df.to_csv(output, index=False)
            return
        df.to_csv(output, index=False, mode='a', header=False)

Utils = Utils()
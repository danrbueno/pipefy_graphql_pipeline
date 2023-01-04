# Run this file in terminal: python run.py "<YOUR PIPE ID>"
# Your pipe id is in the URL (https://app.pipefy.com/pipes/<PIPE_ID>)

import sys
import pipefy

def main(pipe_id):
    pipe = pipefy.Pipe(pipe_id)
    data = pipe.get_data()
    df = pipe.load_dataframe(data)
    print(df)
    
if __name__ == "__main__":
    main(sys.argv[1])
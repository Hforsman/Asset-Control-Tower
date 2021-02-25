"""
These are a bunch of commands used to take a look at the data and get a feel for any 'pollution'
These commands are not meant to be run in any pipeline and are not build to work in the context provided
"""

# Import via pandas.read_csv failed because some lines were too long, others too short
for row in data_list:
    if len(row) != 36:
        print(row)
        print(len(row))

# The too long line is a computer...
for row in data_list:
    if row[4] == "NC6320":
        print(row)
        print(len(row))
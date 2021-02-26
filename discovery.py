"""
These are a bunch of commands used to take a look at the data and get a feel for any 'pollution'
These commands are not meant to be run in any pipeline and are not build to work in the context provided
"""

# Import via pandas.read_csv failed because some lines were too long, others too short
# most issues concatenate the fields type and trim because of wheel sizes in inches ("),
# a few concatenate colour and bodytype probably because of typos
i=0
for row in data_list:
    if len(row) != 36:
        print(row)
        print(len(row))
        i+=1
print(i)

# The too long line is a computer...
for row in data_list:
    if row[4] == "NC6320":
        print(row)
        print(len(row))


source = 'http://www.awitness.org/prophecy.zip' # for unit test on downloading a zip file
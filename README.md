# Instructions on running:
Clone the repository and run "python3 parser.py". Program uses flowlog.txt and lookuptable.txt as input, and output is written to output.txt. To run tests, run "python -m unittest test_parser.py -v".

# Description 
Write a program that can parse a file containing flow log data and maps each row to a tag based on a lookup table. The lookup table is defined as a csv file, and it has 3 columns, dstport,protocol,tag. The dstport and protocol combination decide what tag can be applied.  

# Requirement details 
- Input file as well as the file containing tag mappings are plain text (ascii) files  
- The flow log file size can be up to 10 MB 
- The lookup file can have up to 10000 mappings 
- The tags can map to more than one port, protocol combinations.  for e.g. sv_P1 and sv_P2 in the sample above. 
- The matches should be case insensitive.

# Assumptions made
- This program only supports default log format 
- It does not support custom log format
- Version 2 is the only version supported
- The flowlog, flowlog.txt, has blank lines between each line. This is handled in open_flowlog().
- outputformat.txt contains the general format that the specifications wanted the output to be in.

# Thought Process
Since I know that the dstport and protocol combination are what define the tag, my plan was to read the flowlog file, verify the flowlog version, parse it to obtain the dstport and protocol number, group the corresponding numbers into a tuple, and then return a list of tuples for each line in the flow log.

Then, read the lookup table into a dictionary where the key is a tuple of dstport and corresponding protocol (where the protocol string is converted into its corresponding decimal value through the protocol table dictionary made in open_protocol_table()), and the value is the tag.

Then, when calculating tag counts, iterate through the list of tuples from the flowlog, and try looking it up in the lookup table. If it exists in the lookup table but not in the tag_counts dictionary yet, we can add it to the dictionary. If it exists in the lookup table and the tag_counts dictionary, then we just update the count in the dicitonary. Finally, if the tuple does not exist in the lookup table, than we add the value "Untagged" to the tag_counts if it does not exist already, or increment its value.

Next, with the list of tuples obtained from the flow log, I need to get the second value corresponding to the protocol index, and convert it back into the string representing protocol. So I reversed the protocol table dictionary, and count each combination of port/protocol. Then replace the second value in each tuple with the string representation by performing the lookup in the resersed protocol table.

Finally, with the tag counts and the port/protcol combination counts in list form, I index through the lists and write the desired values into the file output.txt.

# Unit Tests
- There are 5 unit tests in test_parser.py. Each test the five requirements listed towards the top of the README.

# Resources used(provided in specification):
- (https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html)
- Protocol numbers CSV file (protocol-numbers-1.csv) obtained from iana.org site linked in the AWS docs (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
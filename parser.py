import csv

def open_flowlog(flowlog_file = "flowlog.txt"):
    """
    Read the flowlog file, verify version number, and extract destination port and protocol information.

    Returns:
        list: A list of tuples, where each tuple contains:
            - destination port (str) - from the 7th field
            - protocol (str) - from the 8th field

    Note:
        Skips empty lines in the file.
    """
    keyList = []
    with open(flowlog_file, "r", newline="") as file:
        for row in file:
            if not row.strip():
                continue
            spliced_lines = row.split(" ")
            if len(spliced_lines) <= 15 and spliced_lines[0] == '2':
                key = (spliced_lines[6], spliced_lines[7])
                keyList.append(key)
            else:
                print("Only VPC flow log version 2 is supported.")
                exit
    return keyList

def open_protocol_table():
    """
    Open and read the protocol table from a CSV file and create a dictionary mapping protocol names to protocol numbers.

    Returns:
        dict: A dictionary where:
            - keys (str): Protocol names
            - values (str): Protocol numbers (converted to lowercase)

    Example:
        pt_table = open_protocol_table()
        # Returns something like {'hopopt': '0', 'icmp': '1', ...}
    """
    pt_table = {}
    with open("protocol-numbers-1.csv", "r", newline="") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            if row:
                protocol_number = row[1].lower()
                protocol_name = row[0]
                pt_table[protocol_number] = protocol_name
    return pt_table

def open_lt(lookup_file = "lookuptable.txt"):
    """
    Read and process the lookup table from a text file.

    Returns:
        tuple: A tuple containing two elements:
            - dict: Dictionary with (dstport, protocol_number) tuples as keys and corresponding tag values

    Notes:
        - The text file has a header row which is skipped
        - Depends on open_protocol_table() function to convert protocol names to numbers
    """
    protocol_table = open_protocol_table()
    lt_dict = {}
    with open(lookup_file, "r", newline="") as file:
        next(file)
        for row in file:
            row = row.strip()
            lt_lines = row.split(",")
            key_tuple = (lt_lines[0], protocol_table[lt_lines[1].lower()])
            lt_dict[key_tuple] = lt_lines[2]
    return lt_dict

if __name__ == '__main__':
    flowlog = open_flowlog()
    lookup_table = open_lt()
    protocol_table = open_protocol_table()

    #Calculate tag counts.
    tag_counts = {}
    for line in range(len(flowlog)):
        try:
            if lookup_table[flowlog[line]] in tag_counts:
                tag_counts[lookup_table[flowlog[line]]] += 1
            else:
                tag_counts[lookup_table[flowlog[line]]] = 1
        except KeyError:
            if "Untagged" in tag_counts:
                tag_counts["Untagged"] += 1
            else:
                tag_counts["Untagged"] = 1

    tag_count_list = list(tag_counts.items())

    #Calculate unique port/protocol combination.
    reversed_protocol_table = {v: k for k, v in protocol_table.items()}
    combination_counts = {}
    
    for line in flowlog:
        port, protocol = line
        if (port, protocol) not in combination_counts:
            combination_counts[(port, protocol)] = 1
        else:
            combination_counts[(port, protocol)] += 1

    combination_list = list(combination_counts.items())

    for i in range(len(combination_list)):
        combination_list[i] = (combination_list[i][0][0], reversed_protocol_table[combination_list[i][0][1]], combination_list[i][1])

    #Write output to text file.
    with open("output.txt", "w") as file:
        file.write("Tag Counts:\n")
        file.write("Tag,Count\n")
        for i in range(len(tag_count_list)):
            file.write(f"{tag_count_list[i][0]},{tag_count_list[i][1]} \n")
        file.write("\n")
        file.write("Port/Protocol Combination Counts: \n")
        file.write("Port,Protocol,Count\n")
        for i in range(len(combination_list)):
            file.write(f"{combination_list[i][0]},{combination_list[i][1]},{combination_list[i][2]} \n")
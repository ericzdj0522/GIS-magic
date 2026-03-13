import yaml

# This is a simple script to auto update network yaml based on survey stations list:
# input: 1. Surveyed stations list csv. 2. Network.yaml file
def read_and_sort_yaml(region):
    network_file_path = '/Users/dj/Documents/Skylark/skylark-networks/networks.yaml'
    network_file_path_test = '/Users/dj/Documents/Skylark/skylark-networks/networks_test.yaml'
    with open(network_file_path, 'r') as file:
        # Load yaml file into dictionary
        data = yaml.load(file, Loader=yaml.Loader)
        print(data)
        dataset = data['conus']['prod']
        # precheck if station has duplicates
        duplicate_count = validate_yaml('conus', dataset)
        # Sort yaml file based on alphabetic order
        sorted_data = insert_yaml('conus', dataset)
        data['conus']['prod'] = sorted_data

        # Enforce flow style to deepiest level of dictionary
        with open(network_file_path_test, 'w') as file:
            # Custom representer for the 'address' dictionaries to enforce flow style
            def flow_style_identifier_representer(dumper, data):
                # Enforce flow style for this dictionary (identifier)
                items = data.items()
                return dumper.represent_mapping('tag:yaml.org,2002:map', items, flow_style=True)

            # Apply flow style only for 'address' fields
            class CustomDumper(yaml.SafeDumper):
                def represent_data(self, data):
                    if isinstance(data, dict) and 'identifier' in data:
                        # If this is an 'address' dictionary, use flow style
                        return flow_style_identifier_representer(self, data)
                    return super().represent_data(data)




            yaml.Dumper.ignore_aliases = lambda *args: True
            yaml.dump(data, file, Dumper=CustomDumper, default_flow_style=False, sort_keys=False, indent=2)


    print(data['conus']['prod'])


# Validate yaml file for duplicate record before insertion
def validate_yaml(region, target):
    demo = [{'identifier': 'ZBZB00USA'}, {'identifier': 'ZBZB03USA'}, {'identifier': 'ZBZB05USA'},{'identifier': 'SBSB00USA'}]
    duplicate = 0
    # check if station exit in yaml:
    if region == 'conus':
        for item in demo:
            if item in target['base'] or item in target['integrity-primary'] or item in target['integrity-secondary']:
                duplicate += 1

    print(duplicate)
    return duplicate



# Insert new stations to network yaml based on usage case
def insert_yaml(region, target):
    demo = [{'identifier': 'ZBZB00USA'}, {'identifier': 'ZBZB03USA'}, {'identifier': 'ZBZB05USA'}, {'identifier': 'SBSB00USA'}]
    # Insertion based on region, conus for base, integrity-primary, integrity-secondary
    if region == 'conus':
        target['base'].extend(demo)
        target['base'].sort(key=lambda x: x['identifier'])
        target['integrity-primary'].extend(demo)
        target['integrity-primary'].sort(key=lambda x: x['identifier'])
        target['integrity-secondary'].extend(demo)
        target['integrity-secondary'].sort(key=lambda x: x['identifier'])

    return target

    # check if station inserted or not
    print('test')


# Test function
def temp_test_function():
    network_file_path = '/Users/dj/Documents/Skylark/skylark-networks/networks.yaml'
    network_file_path_test = '/Users/dj/Documents/Skylark/skylark-networks/networks_selection.yaml'
    with open(network_file_path, 'r') as file:
        data = yaml.load(file, Loader=yaml.Loader)
        dataset = data['conus']['prod']['integrity-secondary']
        totallist = ''
        for item in dataset:
            antennaid = item['identifier'][5]
            if int(antennaid) % 2 == 0:
                totallist = totallist + "'" + item['identifier'][0:4] + "'" + ','
                print(item['identifier'])

        print(totallist)


if __name__ == '__main__':
    read_and_sort_yaml('conus')

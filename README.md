# xefind

Author: [Carlo Fuselli](mailto:cfuselli@nikhef.nl)

A package to answer all your questions on how and where to find data for the XENONnT experiment.

- Got a list of runs and want to find the availability in every context and environment?
- Want to easily find out which runs are in the latest context for a given source and science run?
- You just have a run_id and want to know everything about it?
- Want to check all the combinations of environments and contexts, and the relative strax, straxen and cutax versions? 
- You are just curious about lineage changes in different environments? 

This package is for you!

## Installation

To install this package, navigate to the root directory of the package and run:

```bash
pip3 install .
```

This will install the package and its dependencies.

## Usage

The only thing you need to run this is the credentials to access the database, which are stored for you autoamtically on midway and dali and that utilix will source for you. 

Here's an example of how to use the find function in this package:

### From single run_id

To get info on a single run id, run:

```bash
python3 find.py peak_basics --run_id 050001
```

### From file with multiple run_ids

To get info on a list of run ids, create a file with the run_ids. 
Each run_id should be on a new line. 
Then run:

```bash
python3 find.py peak_basics --filename runlist_example.txt
```

### From science_run and source

You can also define a science run and source. The run_ids will be queried from the database. 
Try running:

```bash
python3 find.py peaklets --science_run sr1 --source rn-220
```

remember that for background the source is 'none'.

You can also specify mulptiple sources and science runs:

```bash
python3 find.py event_info --science_run sr0 sr1 --source rn-220 none
```

this will give you the result for all combinations of science runs and sources.

### Extra options

By default the output will be printed giving you the availability in the usual dali and midway user disks.
If you want to check a special rucio RSE where the data is stored, you can specify it with the `--extra_location` option.


## Output

The output will be a table with the requested information.

```bash
 Checking for PEAK_BASICS in SR0 with source: RN-220

    Context Environment  Total Checked LineageHash straxen strax  cutax UC_DALI_USERDISK UC_MIDWAY_USERDISK UC_OSG_USERDISK
xenonnt_v14   2024.01.1            354  6bdyxhzzfz   2.2.0 1.6.0 1.16.0         0 (0.0%)           0 (0.0%)        0 (0.0%)
xenonnt_v13   2023.11.1            354  6bdyxhzzfz   2.1.5 1.5.4 1.15.5         0 (0.0%)           0 (0.0%)        0 (0.0%)
xenonnt_v12   2023.10.1            354  5mwtxr7xuj   2.1.4 1.5.4 1.15.4         0 (0.0%)        277 (78.2%)      49 (13.8%)
xenonnt_v11   2023.07.1            354  5mwtxr7xuj   2.1.1 1.5.2 1.15.1         0 (0.0%)        277 (78.2%)      49 (13.8%)
 xenonnt_v8   2022.06.3            354  kqwpf3erfx   1.7.1 1.2.3 1.12.0     354 (100.0%)           0 (0.0%)        0 (0.0%)
```

## Contributing

To contribute to this package, please follow these steps:

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Commit your changes
5. Push your changes to your fork
6. Open a pull request



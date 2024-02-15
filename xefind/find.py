import os
import pandas as pd
from utilix import xent_collection
from datetime import datetime
import argparse

# These are the recommended combinations 
# of context and environment
RECOMMENDED = {
    'xenonnt_v14': '2024.01.1',
    'xenonnt_v13': '2023.11.1',
    'xenonnt_v12': '2023.10.1',
    'xenonnt_v11': '2023.07.1',
    'xenonnt_v8':  '2022.06.3',
}

# These env versions are only needed if the environment 
# was not updated to the contexts collection
ENV_VERSIONS = {
    'xenonnt_v14': {
        'straxen_version': '2.2.0',
        'strax_version': '1.6.0',
        'cutax_version': '1.16.0'
    }, 
    'xenonnt_v13': {
        'straxen_version': '2.1.5',
        'strax_version': '1.5.4',
        'cutax_version': '1.15.5'
    },
    'xenonnt_v12': {
        'straxen_version': '2.1.4',
        'strax_version': '1.5.4',
        'cutax_version': '1.15.4'
    },
    'xenonnt_v11': {
        'straxen_version': '2.1.1',
        'strax_version': '1.5.2',
        'cutax_version': '1.15.1'
    },
}

# These are the locations for the users
LOCATIONS = [
    'UC_DALI_USERDISK',
    'UC_MIDWAY_USERDISK'
]

SCIENCE_RUNS = {
    'sr0': {'$or': [
                {'tags.name': '_sr0'},
                # we have th232 runs that are kind of SR0, let's include them
                {'source': 'th-232', 'start': {'$lte': datetime(2022, 8, 1)}},
            ]},
    'sr0_ted': {'tags.name': '_sr0_ted'},
    'sr1': {'tags.name': '_sr1_preliminary'},
}


def find(query, projection):
    """
    Find documents in the xent_collection based on the given query and projection.

    Args:
        query (dict): The query to filter the documents.
        projection (dict): The projection to specify which fields to include or exclude.

    Returns:
        list: A list of documents matching the query and projection.
    """
    cursor = xent_collection().find(query, projection)
    runlist = list(cursor)
    return runlist

def get_runs_from_source(science_run, source):
    """
    Get a list of run numbers for a given science run and source.

    Args:
        science_run (str): The science run identifier.
        source (str): The source identifier.

    Returns:
        list: A list of run numbers matching the given science run and source.
    """
    query = SCIENCE_RUNS[science_run]
    query['source'] = source
    projection = {'number': 1}
    runlist = find(query, projection)
    return [doc['number'] for doc in runlist]

def get_lineage_hash(context, environment, data_type):
    """
    Get the lineage hash and versions for a given context, environment, and data type.

    Args:
        context (str): The name of the context.
        environment (str): The tag of the environment.
        data_type (str): The type of data.

    Returns:
        tuple: A tuple containing the lineage hash and versions.
            The lineage hash is a string representing the hash value for the given data type.
            The versions is a dictionary containing the versions of straxen, strax, and cutax.
    """
    ctxs = xent_collection(collection="contexts")
    query = {'name': context, 'tag': environment}
    projection = {f'hashes.{data_type}': 1, 'straxen_version': 1, 'strax_version': 1, 'cutax_version': 1}
    res = ctxs.find_one(query, projection)
    if not res:
        return None, {}
    lineage_hash = res['hashes'].get(data_type)
    versions = {k: res.get(k, 'UNKNOWN') for k in ['straxen_version', 'strax_version', 'cutax_version']}
    return lineage_hash, versions

def get_lineae_hash_from_version(context, versions):
    """
    Retrieves the lineae hash from the specified version and context.

    Args:
        context (str): The name of the context.
        versions (dict): The versions to search for.

    Returns:
        str or None: The lineae hash if found, None otherwise.
    """
    ctxs = xent_collection(collection="contexts")
    query = {**versions, 'name': context}
    projection = {f'hashes.{data_type}': 1}
    res = ctxs.find_one(query, projection)
    if not res:
        return None
    return res['hashes'][data_type]


def read_run_ids_from_file(filename):
    """
    Read run IDs from a file.

    Args:
        filename (str): The path to the file.

    Returns:
        list: A list of integer run IDs read from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    # check if the file exists
    if not os.path.isfile(filename):
        print(f"File {filename} not found")
        return []

    with open(filename, 'r') as file:
        run_ids = file.read().splitlines()
    return [int(run_id) for run_id in run_ids if run_id.isdigit()]

def check_runs_available(data_type, run_ids, extra_location=''):
    """
    Check the availability of runs in the database for a given data type and run IDs.

    Args:
        data_type (str): The type of data to check the availability for.
        run_ids (list): The list of run IDs to check.
        extra_location (str, optional): Additional location to check for runs. Defaults to ''.

    Raises:
        ValueError: If no run IDs are found.

    Returns:
        pandas.DataFrame: A DataFrame containing the availability information for each run ID.
    """

    if not run_ids:
        raise ValueError("No run_ids found")

    docs = []

    for context, env_version in RECOMMENDED.items():
        lineage_hash, versions = get_lineage_hash(context, env_version, data_type)
        if not lineage_hash:
            versions = ENV_VERSIONS[context]
            lineage_hash = get_lineae_hash_from_version(context, versions)

        locations = LOCATIONS
        if extra_location:
            locations.append(extra_location)

        # remove _version from the versions
        versions = {k.split('_')[0]: v for k, v in versions.items()}

        if lineage_hash:
            doc = {
                'Context': context,
                'Environment': env_version,
                'Total Checked': len(run_ids),
                'LineageHash': lineage_hash,
                **versions
            }
        
            for location in locations:
                runs_location = get_runs_from_db(run_ids, data_type, lineage_hash, location)
                doc[location] = f"{len(runs_location)} ({len(runs_location) / len(run_ids) * 100:.1f}%)"

            docs.append(doc)

        else:
            print(f"Lineage hash not found for {context} and {env_version}")
    
    df = pd.DataFrame(docs)
    return df

def get_runs_from_db(run_ids, data_type, lineage_hash, location=None):
    """
    Retrieve a list of run IDs from the database based on the provided criteria.

    Args:
        run_ids (list): A list of run IDs to search for.
        data_type (str): The type of data to match.
        lineage_hash (str): The lineage hash to match.
        location (str, optional): The location to match. Defaults to None.

    Returns:
        list: A list of run IDs matching the criteria.
    """

    coll = xent_collection(collection="runs")
    run_ids = [int(run_id) for run_id in run_ids]

    query = {
        'number': {'$in': run_ids},
        'data': {'$elemMatch': 
            {'type': data_type, 
            'meta.lineage_hash': lineage_hash}
        }
    }

    if location:
        query['data']['$elemMatch']['location'] = location

    res = list(coll.find(query, {'number': 1}))
    return [doc['number'] for doc in res]



def parse_args():
    """
    Parse the command line arguments for the find_available.py script.

    Returns:
        argparse.Namespace: The parsed command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="""
        Check if the data is available for a given list of runs, or for a given source and science run.
        You can provide a file with the run_ids, or use the source and science run to get the run_ids from the db.
        Example from db:   python find_available.py peaklets --science_run sr1 --source none
        Example from file: python find_available.py peaklets --filename /path/to/runs.txt
        """
    )
    parser.add_argument('data_type', type=str, help="The data type to check (e.g. peaklets, event_info, etc)")
    
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--source', type=str, nargs='+', help="The source(s) to check (e.g. none, th-232, etc)")
    source_group.add_argument('--filename', type=str, help="The file with the run_ids to check")
    source_group.add_argument('--run_id', type=str, help="The single run_id to check")
    
    parser.add_argument('--science_run', type=str, nargs='+', help="The science run(s) to check (e.g. sr0, sr1, sr)", choices=SCIENCE_RUNS.keys(), default=['sr0', 'sr1'])
    parser.add_argument('--extra_location', type=str, default=None, help="Add extra location on top of UC_DALI_USERDISK and UC_MIDWAY_USERDISK")
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    data_type = args.data_type
    extra_location = args.extra_location

    print("\n", "-"*80)

    # Check for data_type from file if filename is provided
    if args.filename:
        print(f" Checking for {data_type.upper()} from file: {args.filename}\n")
        run_ids = read_run_ids_from_file(args.filename)
        df = check_runs_available(data_type, run_ids, extra_location)
        print(df.to_string(index=False), "\n")

    # Check for data_type with given source and science run
    elif args.source:
        for science_run in args.science_run:
            for source in args.source:
                print(f" Checking for {data_type.upper()} in {science_run.upper()} with source: {source.upper()}\n")
                run_ids = get_runs_from_source(science_run, source)
                df = check_runs_available(data_type, run_ids, extra_location)
                print(df.to_string(index=False), "\n")

    # Check for data_type with given run_id
    elif args.run_id:
        print(f" Checking for {data_type.upper()} for run_id: {args.run_id}\n")
        run_ids = [int(args.run_id)]
        df = check_runs_available(data_type, run_ids, extra_location)
        print(df.to_string(index=False), "\n")

    else:
        raise ValueError("No source, filename, or run_id provided")

    print("-"*80, "\n")


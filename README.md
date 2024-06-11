# gcn-classic-to-json

Convert GCN Classic notices to JSON.

## Configuration

The following environment variables may be used to configure the service:

| Name                 | Value                                                                              |
| -------------------- | ---------------------------------------------------------------------------------- |
| `KAFKA_*`            | Kafka client configuration as understood by [Confluent Platform docker containers] |

[Confluent Platform docker containers]: https://docs.confluent.io/platform/current/installation/docker/config-reference.html

## How to contribute

This package uses [Poetry](https://python-poetry.org) for packaging and Python virtual environment management. To get started:

1.  [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and [clone](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#cloning-your-forked-repository) this repository.

2.  Install Poetry by following [their installation instructions](https://python-poetry.org/docs/#installation).

3.  Install this package and its dependencies by running the following command inside your clone of this repository:

        poetry install --all-extras

## How to add notice types

For a mostly complete example, see https://github.com/nasa-gcn/gcn-classic-to-json/tree/main/gcn_classic_to_json/notices/SWIFT_BAT_GRB_POS_ACK.

1.  Create a new subdirectory in https://github.com/nasa-gcn/gcn-classic-to-json/tree/main/gcn_classic_to_json/notices with a name corresponding to the GCN Classic notice type.

2.  Save a specimen of the 160-byte format GCN Notice in that directory under the filename `example.bin`. Some directories are pre-populated with recent specimens.

3.  Add a file called `__init__.py` to that directory. In that file, define a single Python function which takes the an array of 40-byte integers as input and returns a dictionary as output. See [GCN Classic documentation](https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html) for an explanation of the binary field layout.

4.  Run `pytest --generate` to run the test suite with and generate the expected output JSON file for your new notice type. It will create a new file called `example.json` in your new directory.

5.  Adjust your parser and repeat the previous step until the `example.json` file is perfect.

6.  [Create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) to add the new directory.

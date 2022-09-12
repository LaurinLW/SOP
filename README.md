# Experiment

## Setup
We recommend a Postgresql database for production use. SQLite databases will be deleted when the docker container is restarted.
The database should be set up, and the correct settings included in the `settings.py` file before continuing. The file can be found at `webserver/sop/settings.py`. A comma must follow the last entry in the ALLOWED_HOSTS setting.

Most things can be set up using the setup script.
It requires python 3 and the python docker package to run.

Run `python setup.py setup` to start the setup process. This will create all required docker volumes, docker networks, and docker images.
Once the setup is complete, you can start the project using `python setup.py start`.

You can use `python setup.py stop` to stop the running web server container and all running experiment containers.

Standard users can be created using the register form on the website. Superusers can be created using the `create_admin.sh` script. Just run the script when the web container is online and follow the instructions.

## Metric
The `metric` class is the base class for all metrics. It contains two abstract methods. The first is the `__init__` functions. It takes a version object as an additional parameter. This version object is the version the metric should process.

The second function is `filter(self, filterString: string = '')`. The filter string is passed directly from the user input. The syntax is determined by the metric. An example of a filterstring syntax can be found in the TestMetric.

When the metric is accessed, a new instance will be created first. Next, the filter method is called. After that, the metric has to have a member called _view of the type `MetricView`. This view is used to visualize the data. There are currently 2 types of visualization: GraphView (bar and line graphs) and TableView for tabular data. The ErrorView should be used when an error occurs while processing.

Metrics need to be exported by the sop.metrics package to be displayed on the website. This can be done in the `__init__.py` file.

## Metric Usage
There are currently 3 metrics implemented. The LineMetric's only purpose is to show the. The data is just dummy data.

The AlgoMetric shows the types of Algorithms selected for this experiment in a bar graph.

The TestMetric is the most complex one. The first columns show the dataset. The last 5 columns show the number of algorithms that classify the datapoint as an outlier grouped by algorithm type. Without any filtering, all data points in the 95th percentile are considered outliers. Using the filter options, you can change that threshold. Typing `threshold=0.5;` would, for example, change that threshold to the 50th percentile.

You can also apply query and select operations on the dataset. An example would be `select=Column1;query=Columns1>0`.
You can, of course, mix the 3 arguments as you like.
## Custom Algorithms
Custom algorithms must implement the pyod BaseDetector model (pyod.models.base.BaseDetector) interface.
## The Experiment
The Experiment can be run as a standalone CLI Application. To run the Experiment without a server the -debug flag must be selected. In this case -id and -c are disregarded but still required.
The arguments are as follows:
- -d (str): Working directory with all files relevant to the experiment.
- -s (int): seed for rng
- -minsd (int): minimal subspace dimension
- -maxsd (int): maximal subspace dimension
- -ns (int): number of subspaces
- -id (str): unique identifier of the experiment
- -c (str): server url
- -p (int): number of processes for parallel execution, default 1
- -debug: enables debug mode, redirects server messages to console

An example call would be:
```bash
python experiment/experimentmain.py -d /absolute/path/to/dir -s 46290 -minsd 5 -maxsd 10 -ns 20 -id test -c irrelevant -debug -p 6
```
If you want to run the experiment you usually(at least on our machines) have to add the directory containing the experimentmain.py file to your python path.

The directory must have following structure:<br>
```
dir
├── algorithms
│   ├── parameters.json
│   └── useralgorithms
│       └──useralgo1.py
│       └──useralgo2.py
└── dataset.csv
```

The files:
- parameters.json: A json File containing the full import path a model and it's parameters. If the parameters are empty the default parameters will be selected.
```json 
{"pyod.models.knn.KNN":{
    "contamination": 0.1,
    "n_neighbors": 5,
    "method": "largest",
    "radius": 1,
    "algorithm": "auto",
    "leaf_size": 30,
    "metric": "minkowski",
    "p": 2,
    "metric_params": null,
    "n_jobs": 1
    }, 
"pyod.models.abod.ABOD":{}}
```
- dataset.csv: The dataset. The name of this file can be arbitrary but it must end with ".csv". The csv file must use the "," character as the seperator.
- useralgox.py: see above section about custom algorithms

The Output:
The output will be written to the "export" directory in the directory passed as parameter. The "export" directory will be created if it does not already exist. The Result files will be overwritten but not deleted if the experiment is run again with the same experiment.
The Result files are csv files containing: the subspace, the model's outlier scores and errors related to models.
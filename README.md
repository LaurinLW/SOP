# Experiment

## Setup
We recommend a Postgresql database for production use. SQLite databases will be deleted when the docker container is restarted.
The database should be set up, and the correct settings included in the `settings.py` file before continuing. A semicolon must follow the last entry in the ALLOWED_HOSTS setting.

Most things can be set up using the setup script.
It requires python 3 and the python docker package to run.

Run `python setup.py setup` to start the setup process. This will create all required docker volumes, docker networks, and docker images.
Once the setup is complete, you can start the project using `python setup.py start`.

You can use `python setup.py stop` to stop the running web server container and all running experiment containers.

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
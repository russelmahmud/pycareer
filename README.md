## PyCareer Website (https://www.pycareer.com/)

### Setup and run locally
1. Install the [App Engine Python SDK](https://cloud.google.com/sdk/downloads). You'll need Python 2.7, [pip 1.4 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

2. [Optional] Mac OSX only
```
$ xcode-select --install
```

3. Install dependencies
```
$ sudo pip install lxml==2.3.5
$ sudo pip install pillow==2.9.0
$ pip install -t lib -r requirements.txt
```

4. Run this project locally from the command line:
```
$ dev_appserver.py . --datastore_path=database
OR
$ dev_appserver.py . --log_level=debug --enable_sendmail
```
See the output in your browser at [http://localhost:8080](http://localhost:8080)

5. To create superuser, visit following url in browser. `user/pass: russel/russel`
```
http://localhost:8080/load_data/
```

### Setup test environment
1. Create virtualenv and activate it
```
$ virtualenv venv --system-site-packages
$ source venv/bin/activate
```

2. Install dependencies
```
$ pip install -r requirements_dev.txt
```

3. Add google_appengine path in `~/.bash_profile`
```
export PATH=$PATH:~/google-cloud-sdk/platform/google_appengine
```

4. To run test
```
$ py.test tests/
```


### Deploy
To deploy the application:

1. Use the [Admin Console](https://appengine.google.com) to create an app.
2. Replace `python-career` in `app.yaml` with the app id from the previous step.
3. ```gcloud app deploy app.yaml [--project=python-career] [--version=dev/prod] [--verbosity=info]```
4. Congratulations! Your application is now live at `https://python-career.appspot.com`.
4. To rebuild index ```gcloud app deploy index.yaml [--project=python-career] [--version=dev/prod] [--verbosity=info]```
```
See Indexing upate here
https://console.cloud.google.com/datastore/indexes?project=python-career
```

### Datastore
`djangoappengine` provides built-in support for App Engine's NoSQL datastore.
See the documentation for [supported and unsupported features](http://djangoappengine.readthedocs.org/en/latest/db.html)
from the core Django library.

### Installing Libraries
See the [third-party
libraries](https://developers.google.com/appengine/docs/python/tools/libraries27)
page for libraries that are already included in the SDK. To include SDK
libraries, add them in your app.yaml file. Other than libraries included in
the SDK, only pure python libraries may be added to an App Engine project.

### Important Links
1. [Google Developer Console](https://console.developers.google.com/project/python-career)
2. [Google Analytics](https://www.google.com/analytics/web/)
3. [Google Webmaster Tool](https://www.google.com/webmasters/tools/)
4. [Google App Engine](https://appengine.google.com)

#### To Do
* Integrate Python Events (http://lmorillas.github.io/python_events/)
* Gulp (deploy/test/build)
* MixPanel Integration (User Behaviour)

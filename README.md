# Streamango

Python wrapper for [streamango.com API](https://streamango.com/api "Streamango API")

## Install

``` bash

    $ pip install git+https://github.com/odysseusmax/PyStreamango.git
```


## Usage


All `API` features are implemented.

**Retrieve account info**

``` python

    from streamango import Streamango

    sm = Streamango('login', 'key')

    account_info = sm.account_info()
    print(account_info)
```


**Upload file**

``` python

    from streamango import Streamango

    sm = Streamango('login', 'key')

    uploaded_file_info = sm.upload_file('/home/username/file.txt')
    print(uploaded_file_info)
 ```


**Retrieve file info**

``` python

    from streamango import Streamango

    sm = Streamango('login', 'key')

    # Random file id.
    file_id = 'YMTqhQAuzVX'

    file_info = sm.file_info(file_id)
    print(file_info)
```

## Documentation


Documentation is not available currently.

## Note


Forked from [PyOpenLoad](https://github.com/mohan3d/PyOpenload) and adapted to work with Streamango API

# Shaper

[![Latest version](https://img.shields.io/pypi/v/shaper.svg)](https://pypi.org/project/shaper/)
[![License](https://img.shields.io/badge/license-Apache-green.svg?style=flat)](https://raw.githubusercontent.com/arno49/shaper/master/LICENSE)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/arno49/shaper.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/arno49/shaper/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/arno49/shaper.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/arno49/shaper/context:python)
[![codecov](https://codecov.io/gh/arno49/shaper/branch/master/graph/badge.svg)](https://codecov.io/gh/arno49/shaper)
[![Build Status](https://travis-ci.org/arno49/shaper.svg?branch=master)](https://travis-ci.org/arno49/shaper)

Tool for render configurations from few templates/sources.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Installing

Install via [pypi](https://pypi.org/project/shaper/):

```
pip install shaper
```


### Use cases
Aim of shaper - make configuration management easier with templating, DSL and CMDBs.


#### Step 1 - Convert existing project configurations to DSL

```
cd myproject
shaper read
```

We will get `out.yml` file with DSL of our project configuration

<details><summary>out.yml</summary>
<p>

```python
my-backend:
  src:
    main:
      resources:
        application-dev1.properties:
          spring.cache.type: 'redis'
          spring.redis.host: 'dev1.111111.0001.use1.cache.amazonaws.com'
          spring.redis.port: '6379'
          spring.redis.ssl: 'false'
          spring.redis.ttl.minutes: '30'
          spring.redis.database: '0'
          spring.redis.available: 'true'
          app.init.enabled: 'true'
          app.email.support_address: 'support@my-domain.com'
          app.email.default_from: 'no-replay@my-domain.com'
          app.lock.provider: 'redis'
        application-qa1.properties:
          spring.cache.type: 'redis'
          spring.redis.host: dev1.111111.0001.use1.cache.amazonaws.com
          spring.redis.port: '6379'
          spring.redis.ssl: 'false'
          spring.redis.ttl.minutes: '30'
          spring.redis.database: '0'
          spring.redis.available: 'true'
          app.init.enabled: 'true'
          app.email.support_address: 'support@my-domain.com'
          app.email.default_from: 'no-replay@my-domain.com'
          app.lock.provider: 'redis'
        application-prod1.properties:
          spring.cache.type: 'redis'
          spring.redis.host: dev1.111111.0001.use1.cache.amazonaws.com
          spring.redis.port: '6379'
          spring.redis.ssl: 'false'
          spring.redis.ttl.minutes: '30'
          spring.redis.database: '0'
          spring.redis.available: 'true'
          app.init.enabled: 'true'
          app.email.support_address: 'support@my-domain.com'
          app.email.default_from: 'no-replay@my-domain.com'
          app.lock.provider: 'redis'
        application.properties:
          app.init.enabled: 'true'
```

</p>
</details>


#### Step 2 - Agregate common parameters with YAML anchor/alias

Using YAML specification let's rewrite duplicating data with anchors/aliases

<details><summary> out_refactored.yml </summary>
<p>

```python
mappings.yml:
  redis:
    - host: &redis_dev_host 'dev.111111.0001.use1.cache.amazonaws.com'
      db:
        dev1: &redis_dev1_dbname 0
        qa1: &redis_qa1_dbname 1

    - host: &redis_prod_host 'prod.0000000.0001.use1.cache.amazonaws.com'
      db:
        prod1: &redis_prod1_dbname 0
    
  common_properties: &common_properties
    spring.cache.type: 'redis'
    spring.redis.port: '6379'
    spring.redis.ssl: 'false'
    spring.redis.ttl.minutes: '30'
    spring.redis.available: 'true'
    app.init.enabled: 'true'
    app.email.support_address: 'support@my-domain.com'
    app.email.default_from: 'no-replay@my-domain.com'
    app.lock.provider: 'redis'

my-backend:
  src:
    main:
      resources:
        application-dev1.properties:
          <<: *common_properties
          spring.redis.host: *redis_dev_host
          spring.redis.database: *redis_dev1_dbname

        application-qa1.properties:
          <<: *common_properties
          spring.redis.host: *redis_dev_host
          spring.redis.database: *redis_qa1_dbname

        application-prod1.properties:
          <<: *common_properties
          spring.redis.host: *redis_prod_host
          spring.redis.database: *redis_prod1_dbname

        application.properties:
          app.init.enabled: 'true'
```

</p>
</details>

This datastructure after loads equal to previus version, but look much more pretty without duplicates parameters.


#### Step 3 - Write properties from CMDB

```
shaper write out_refactored.yml
```


#### Step 4 - Enjoy

Check diff with existing configuration, fix if something wrong and embed into your CD pipeline.


## Running the tests
We are using tox to agregate all testing steps. Just run it in project repository. All merges runs tests in [travis](https://travis-ci.org/arno49/shaper). 

```
tox
```


## Contributing

If you want to contribute to a project and make it better, your help is very welcome. Contributing is also a great way to learn more about social coding on Github, new technologies and and their ecosystems and how to make constructive, helpful bug reports, feature requests and the noblest of all contributions: a good, clean pull request.

### How to make a clean pull request

Look for a project's contribution instructions. If there are any, follow them.

- Create a personal fork of the project on Github ([howto](https://help.github.com/articles/fork-a-repo/)).
- Clone the fork on your local machine. Your remote repo on Github is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.
- Create a new branch to work on! Branch from `develop` if it exists, else from `master`.
- Implement/fix your feature, comment your code.
- Follow the code style of the project, including indentation.
- If the project has tests run them!
- Write or adapt tests as needed.
- Add or change the documentation as needed.
- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on Github, the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `develop` branch if there is one, else go for `master`!
- If the maintainer requests further changes just push them to your branch. The PR will be updated automatically.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete
your extra branch(es).

And last but not least: Always write your commit messages in the present tense. Your commit message should describe what the commit, when applied, does to the code – not what you did to the code.

## Versioning

We use [versioneer](https://pypi.org/project/versioneer/) for versioning. For the versions available, see the [tags on this repository](https://github.com/arno49/shaper/tags).

## Authors

* **Ivan Bogomazov** - [arno49](https://github.com/arno49)

See also the list of [contributors](https://github.com/arno49/shaper/graphs/contributors) who participated in this project.

## License

This project is licensed under the Apache 2.0 - see the [LICENSE](LICENSE) file for details


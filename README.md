# Automated Usability Test

## Before start

You need:

- A computer with `Windows 10` as operating system

- `SciTools Understand` installed
  > Apply for a free student license on the [website](https://www.scitools.com/student/) if you don't have a one.

- `Sourcetrail` installed
  > Follow the guidance on [tools/#_INSTALL_THIS_sourcetrail/README.doc](./tools/%23_INSTALL_THIS_sourcetrail/README.doc) to install and operate.

- Allow git to use long file name:

  ```sh
  $ git config --system core.longpaths true
  ```

## Run test, with only one command

```sh
$ python do.py <lang> <range>
```

where,

* `lang` can be one of
  * `java`
  * `cpp`
  * `python`

* `range` can be one of
  * a number `n`, refers to n-th project in the list
  * a range `a-b`, refers to projects from  a-th to b-th

Boom, you are free to afk.

## Submit results

We want newly generated files under these directories:

* `logs/`
* `time-records/`

# Automated Usability Test

## Before start

You need:

- A computer with `Windows 10` as operating system

- `Java` latest installed (>= 15) and can be accessed via environment path
  > Some tools depends on JRE to run.

- `SciTools Understand` installed and can be accessed via environment path
  > Apply for a free student license on the [website](https://www.scitools.com/student/) if you don't have a one.

- `Sourcetrail` installed
  > Follow the guidance on [tools/#_INSTALL_THIS_sourcetrail/README.doc](./tools/%23_INSTALL_THIS_sourcetrail/README.doc) to install and operate.

- Allow git to use long file name:

  ```sh
  $ git config --system core.longpaths true
  ```

## Run test, with only one command

```sh
$ python do.py <lang> <range> [only]
```

where,

* `lang` can be one of
  * `java`
  * `cpp`
  * `python`

* `range` can be one of
  * a number `n`, refers to n-th project in the list
  * a range `a-b`, refers to projects from  a-th to b-th

> * Usually you don't need to set this, `only` can be one of
>   * `enre`: Runs `ENRE-<lang>` only
>   * `depends`: Runs `Depends` only
>   * `understand`: Runs `Understand` only
>   * `clone`: Just clone the repositories

We highly encourage you to run this script under `Windows Terminal` + `PowerShell`, this conbination suits the modern world on Windows platform.

Press ENTER, Booooooom, you are free to afk.

## Submit results

We want all newly generated files under these directories:

* `logs/`
* `time-records/`

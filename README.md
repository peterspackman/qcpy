# Quantum Chemistry Automaton

[![Build Status](
    https://travis-ci.org/peterspackman/qcpy.svg?branch=master)
    ](https://travis-ci.org/peterspackman/qcpy)

### What:

A simple library to automate creation (and execution) of quantum 
chemistry jobs. Generic enough to handle all kinds of things.

### Installing
Requires python 3.5 (or newer)

```pip install https://github.com/peterspackman/qcpy/archive/master.zip```

### How:

The library is populated by the following basic structures:

* Templates
* Jobs
* Runners

## Templates
For input file based programs we have templates e.g for a g09
single point energy calculation:
```
# {{job.method}}/{{job.basis_set}}

{{job.name}}

{{geom.charge}} {{geom.multiplicity}}
{%- for line in geom.as_lines(line_format="g09") %}
{{ '%s' | format(line)}}
{%- endfor %}
{{'\n'}}
```

## Jobs
Jobs basically consist of running a calculation, with optional
dependencies and postprocessing.

## Runners
Different kinds of 'runners' for running jobs locally,
remotely on PBS/Slurm (planned) etc.

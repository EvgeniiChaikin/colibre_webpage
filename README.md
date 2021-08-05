# Colibre webpage
A package for arranging and visualising Colibre data


Description
--------------

Generates a tree whose leaf nodes are html pages containing plots from COLIBRE (or other projects') runs.
The script assumes that the run directories begin with `z?.?_` prefix where 
the first and second question marks are the first and second digit of the value 
of the redshift at which plots for the respective directory are made.
There is also division into **individual_runs** and **comparisons** sub-trees. The
former contains plots with data from single runs, while in the latter data from 
multiple runs is shown.


Running
--------------

Below is an example of a directory tree on which the script can be run

```
Root_directory
|
|_ comparisons
|   |_ Tab1
|   |   |_ Subtab1
|   |   |   |_z5.0_comparison1
|   |   |_z2.0_comparison2
|   |   |_z5.0_comparison2
|   |_z0.0_comparison3
|_ individual_runs
    |_ Tab1
    |   |_z5.0_run2
    |_ Tab2
        |_z1.0_run1 
        |_z5.0_run1
```

Note that
1. Each leaf of the tree is a directory with no subdirectories. The script expects that it contains `index.html` file with the plots;
2. Names of all leaf nodes must start with `z?.?_` prefix where 
the first and second question marks are the first and second digit of the value 
of the redshift at which plots for the respective directory are made;
3. The root directory must have two subdirectories: `individual_runs` and `comparisons`. The former is for plots from single runs and the latter is for plots from run comparisons;

To run the script, use
```bash
python3 ./webpage_run.py \ 
        -r Root_directory \ # path to the root of the three
        -u dc-cosma-user \ # Name of the user\'s account on cosma. This is needed to run the slurm command to see which runs are ongoing
        -s colibre \ # Pattern in simulation output files
        -z ./output_list.txt\ # Path to file with the redshifts for output files 
        -t Tab1 Tab2  \ # Extra tabs that will be added to the tab bar 
        -o ./output_path \ # Path to directory where the output html page will be saved
        -d  \ # Running in debug mode
```




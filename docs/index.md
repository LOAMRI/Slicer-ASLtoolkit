# ASLtk - Arterial Spin Labeling toolkit

![project logo](assets/asltk-logo.png){ width="350" .center}
Welcome to the ASL toolkit!

This 3D Slicer extension was designed to assist users in processing Arterial Spin Labeling (ASL) MRI images, from basic imaging protocols to the state-of-the-art models provided in the scientific literature.

The major objective of this project is to give an open-source alternative to researchers in the MRI field.

The full documentation of the usage, implementation and updates in the `asltk` library is given in this repository and posted online using a [web-based host](https://asltk.readthedocs.io/en/main/). 


## Output examples

The ASLtoolkit extension is a simple way to collect ASL quantitatve output mappings using a GUI interface. The images below represents some examples:

![CBF map](assets/cbf_map.png){ width="300" .center}
A CBF map example, using multi PLD ASL imaging acquisition

![ATT map](assets/att_map.png){ width="300" .center}
A ATT map example, using multi PLD ASL imaging acquisition

![T1 blood-GM map](assets/t1_blood_gm_map.png){ width="300" .center}
A T1 blood-GM map example, using the Multi TE ASL imaging acquisition


## Modules

### CBF ATT

This module is able to reconstruct the `CBF` and `ATT` maps from a ASL imaging acquisition.

### Multi TE ASL

This module is able to reconstruct the `T1 blood-GM` map from a multi echos (TE) ASL imaging acquisition.

## How to use

The `ASLtoolkit` extension can be used directly from the modules in the 3D Slicer module list. Hence, the user can select the required information and also start the mapping calculation. When it is finished, the data is loaded in the Slicer scene viewer.

## How to install

The ASL toolkit extension can be found directly from the Slicer Extension Manager. Search for `ASL toolkit` in the extension browser and select install.

!!! warning
    This extension is offered, firstly, by the `nightly` Slicer version and then, after a compatibility verification has been performed, it is added to the Slicer `stable` version.

### Quick tutorial

To assist new users in the usage of the ASL toolkit extension, please follow this simple tutorial:

1. Download the sample data (hosted at a [public link from Google Drive](https://drive.google.com/file/d/1agtHY9SLvC9975L6H0RL6PfIHATnJKcI/view))

    - This dataset sample is a pCASL ASL image with a text file giving the PLD, LD and TE values as comma-separated lists
  
2. After the dataset sample download, uncompress the zip file to a local folder

3. Open Slicer with the ASL Toolkit extension being already installed

    - Installation instruction is given in the How to install section above.
  
4. Search for the `CBF and ATT` or `Multi TE ASL` modules

    - To search for the module one can use the dropdown module list and look at it manually or use the module search toggle.
  
5. Once the module GUI is shown, fill in the indicated information and press run

!!! info
    The `asltk` [Python package](https://pypi.org/project/asltk/) is used in background. If the Slicer Python interpreter do not have the `asltk` package installed, then it will be made automatically.

!!! tip
    The `asltk` package has multitheading algoritm performance. Depending on the machine configuration and capability, the processing time can very considerably. See more details about it on the `asltk` [documentation](https://asltk.readthedocs.io/en/main/).

## Cite this tool

We hope that the `ASLtoolkit` can be helpful for your applications. If possible, recall to cite at least one of the following publications:

* Senra Filho, A. C. ; Paschoal, A. M. "Open-Source Multi-Echo (TE) MRI Tool for Arterial Spin Labelling Imaging Protocols". ISMRM & ISMRT Annual Meeting (2025). [Link](https://www.researchgate.net/publication/394469211_Open-Source_Multi-Echo_TE_MRI_Tool_for_Arterial_Spin_Labelling_Imaging_Protocols)

## License

This project is under MIT license and following details are given at the [LICENSE](https://github.com/LOAMRI/Slicer-ASLtoolkit/blob/main/LICENSE) file in the project repository.

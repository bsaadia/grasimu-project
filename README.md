# What is GRASIMU?

Forward modelling of gravity signals is useful for designing an effective survey over a potential target. Given how ubiquitous gravimetry is in mineral exploration, archaeology, and planetary geosciences, there is a need for a fast, open-source tool that can model a 3D target of complex geometry in any terrain environment.

GRASIMU is a browser-based tool written in Python and designed for geoscientists and students. It is meant for educational purposes *only*.

It contains four main components: i) target upload and configuration, ii) terrain generation, iii) survey design, and iv) an interactive visualization dashboard. Throughout each stage, 2D and 3D visualizations are given as results are calculated to allow for near-real-time modifications to parameters.

It is licensed for use under GNU General Public License v3.0. We welcome bug reports, modifications, and improvements to the program. Comprehensive documentation coming soon.

### Acknowledgments

The initial version of the program was developed with funding from:
* European Space Agency SysNova Lunar Caves Programme
* NSERC Engage

The authors (Benjamin Saadia, Frank De Veld, and Shona Birkett) also thank Dr. Alexander Braun for his tests and suggestions.


# GRASIMU Instructions

## Getting Started

Get set up locally in two steps:

### Setup Secret Key

Replace the SECRET_KEY variable in **.env.example** with your own password and rename this file to **.env**.

Flask "secret keys" are random strings used to encrypt sensitive user data, such as passwords. While this version of GRASIMU does not require encryption, future versions might.

*Remember never to commit secrets saved in .env files to Github.*

### Installation

*Note: The following installation instructions have been tested on macOS Big Sur 11.2 (running through Rosetta), Ubuntu 20.04 running in a virtualbox on Windows 10, and a clean install of Fedora32. While all components will work directly on Windows, there is not yet an easy install method.*
*GRASIMU was designed in Python 3.8 and does not yet work on 3.9 due to dependencies not being released for that version yet. Consider using a package like pyenv to manage your python version within the project's virtual environment.*

A FORTRAN compiler like gcc is required to use GRASIMU, and must be installed separately.

Get up and running with `make deploy`. This will install all of the dependencies. 

```shell
$ git clone https://github.com/bsaadia/grasimu-project
$ cd grasimu-project
$ make deploy
``` 

## Run GRASIMU

To run the applet after this initial install, simply type:

```shell
$ make run
``` 


## Disclaimer

The information contained in the applet is for general information purposes only. While we strive to keep the information up-to-date and correct, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the website or the information, products, services or related graphics contained on the website for any purpose. Any reliance you place on such information is therefore strictly at your own risk.

In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from, or in connection with, the use of this website.
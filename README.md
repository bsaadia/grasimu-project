# GRASIMU Instructions

# Getting Started

Get set up locally in two steps:

### Setup Secret Key

Replace the SECRET_KEY variable in **.env.example** with your own password and rename this file to **.env**.

Flask "secret keys" are random strings used to encrypt sensitive user data, such as passwords. While this version of GRASIMU does not require encryption, future versions might.

*Remember never to commit secrets saved in .env files to Github.*

### Installation

Get up and running with `make deploy`. This will install all of the dependencies. A FORTRAN compiler like gcc is required to use GRASIMU, and must be installed seperately.

```shell
$ git clone https://github.com/bsaadia/grasimu-project
$ cd grasimu-project
$ make deploy
``` 

### Run GRASIMU

To run the applet after this initial install, simply type:

```shell
$ make run
``` 


### Disclaimer

The information contained in the applet is for general information purposes only. While we strive to keep the information up-to-date and correct, we make no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the website or the information, products, services or related graphics contained on the website for any purpose. Any reliance you place on such information is therefore strictly at your own risk.

In no event will we be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from, or in connection with, the use of this website.
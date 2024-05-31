
# parseagrave

This is a python-based application that prompts user for a grave ID from findagrave.com and will find the birthdate and place, deathdate and place, parents, siblings and spouses for that ID. It then recursively gets the same information for all parents until no more parents are identified. The results are output in a json-formatted file.


## Badges

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)


## Authors

- [@wrestleraaron](https://github.com/wrestleraaron)


## Run Locally

Clone the project

```bash
  git clone https://github.com/wrestleraaron/parseagrave
```

Go to the project directory

```bash
  cd parseagrave
```
Optional create a virtual python environment and activate it:

```bash
python -m venv venv
. venv/activate (Unix/Mac)
venv\scripts\activate (Windows)
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Run the application

```bash
  python graves.py
```
You will need the grave ID from findagrave.com url (e.g. https://www.findagrave.com/memorial/66870391/thomas_packard - you would use 66870391)
You will also be prompted for an output filename (filename only, the file is output to the current working directory)

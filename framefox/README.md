# Test in dev mod

first: create and activate your venv  
cd framefox (to see the toml file)  
pip install -e .  
  
try: framefox  

# Put lib on PyPi test

## Create all files

pip install twine wheel  
python setup.py sdist bdist_wheel  
twine upload --repository-url <https://test.pypi.org/legacy/> dist/*  

## Install from PyPi

pip install --index-url <https://test.pypi.org/simple/> --extra-index-url <https://pypi.org/simple/> framefox  

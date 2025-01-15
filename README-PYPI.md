# Test in dev mod

first: create and activate your venv  
pip install -e .  
  
try: framefox  

# Put lib on PyPi test

## Create all files

pip install twine wheel  
python setup.py sdist bdist_wheel  
twine upload --repository-url <https://test.pypi.org/legacy/> dist/*  
or  
twine upload --repository-url <https://test.pypi.org/legacy/> dist/* -u __token__ -p <votre_cle_api>

## Install from PyPi

pip install --index-url <https://test.pypi.org/simple/> --extra-index-url <https://pypi.org/simple/> framefox  
or  
python3 -m pip install --index-url <https://test.pypi.org/simple/> --extra-index-url <https://pypi.org/simple/> framefox

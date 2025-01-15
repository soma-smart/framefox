# Test in dev mod

first: create and activate your venv  
pip install -e .  
  
try: framefox  

# Put lib on PyPi test

## Create all files

pip install twine wheel  
  
## Upload project on PyPI test

python setup.py sdist bdist_wheel  
twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u __token__ -p <votre_cle_api>
  
or if you have publish_lib.sh  
  
chmod +x publish_lib.sh  
bash publish_lib.sh  
  
## Install from PyPi

windows: pip install --index-url <https://test.pypi.org/simple/> --extra-index-url <https://pypi.org/simple/> framefox  
or  
linux: python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ framefox

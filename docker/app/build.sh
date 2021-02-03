rm -fR py/app
rm -fR py/scripts

cp -r ../../src py/app
cp -r ../../scripts py/scripts

find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "test*.py" -type f -delete

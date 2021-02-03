REM required for installation and script to work !
REM http://cygwin.com/

REM rm -fR py\configs
rm -fR py\app
rm -fR py\scripts
mkdir py
REM cp -r ..\..\configs py\configs
cp -r ..\..\src py\app
cp -r ..\..\scripts py\scripts

find . -name "__pycache__" -type d -exec rm -rf {} +
REM just remove any tests they not needed
find . -name "test*.py" -type f -delete

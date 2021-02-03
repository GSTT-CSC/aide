REM required for installation and script to work !
REM http://cygwin.com/

rm -fR build

cd ../../web/ai_pipeline
call npm run-script build

cd ../../docker/nginx
cp -r ../../web/ai_pipeline/build build

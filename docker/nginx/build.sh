rm -fR build

cd ../../web/ai_pipeline
npm run-script build

cd ../../docker/nginx
cp -r ../../web/ai_pipeline/build build

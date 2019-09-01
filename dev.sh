# python setup.py -q install
# webplatform-cli $@
appinit variables set apps-path ~/git/platform/applications
appinit apps add SupportExceptions
appinit apps disable SupportExceptions
appinit apps add Home
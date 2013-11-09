curl --data "groupname=A" http://50.116.54.133:8080/addgroup
curl --data "username=a" http://50.116.54.133:8080/adduser
curl --data "username=b" http://50.116.54.133:8080/adduser
curl --data "username=c" http://50.116.54.133:8080/adduser
curl --data "username=a&groupname=A" http://50.116.54.133:8080/addtogroup
curl --data "username=b&groupname=A" http://50.116.54.133:8080/addtogroup
curl --data "username=c&groupname=A" http://50.116.54.133:8080/addtogroup
curl --data "username=a&delay=50" http://50.116.54.133:8080/wakeuptime
curl --data "username=a&delay=0" http://50.116.54.133:8080/wakeuptime
curl --data "username=b&delay=20" http://50.116.54.133:8080/wakeuptime
curl --data "username=c&delay=100" http://50.116.54.133:8080/wakeuptime
curl --data "username=a" http://50.116.54.133:8080/getresults
curl --data "username=b" http://50.116.54.133:8080/getresults
curl --data "username=c" http://50.116.54.133:8080/getresults



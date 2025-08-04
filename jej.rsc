:local token "Ut2w7qytQvIhgtjLomoMyw99tqqk97YX"
:local url "http://10.11.11.22:5000/gpiocontrol/reboot"
:local jsonData "{ 'pins': [17, 22, 27] }"
:local header "Authorization: Bearer $token"

/tool fetch url=$url http-header-field=$header http-method=post http-data=$jsonData output=user
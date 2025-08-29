# Extrae datos de los componentes de interes los junta en una variable y los envía a Grid Guardian.

:log info "[Grid Guardian] Comenzando extracción de datos"

# Busca la ip del rasp dinamicamente desde los leases del mismo dispositivo
:local pihost ""
:foreach lease in=[/ip dhcp-server lease print as-value where status="bound"] do={
    :local host ($lease->"host-name")
    :local addr ($lease->"address")
    :if ($host = "raspberrypi") do={
        :set pihost $addr
    }
}

# Configs de la API
:local token # ingresar aquí el token
:local port "5000"
:local endpoint "/guardian/data"
:local url ("http://" . $pihost . ":" . $port . $endpoint)
:local header "Authorization: Bearer $token"

# Realiza la consulta y almacena los datos
:local result [/tool fetch url=$url http-header-field=$header mode=http as-value output=user]
:local content "Sin respuesta"
:if ([:typeof $result] != "nothing" && [:len $result] > 0) do={
    :set content ($result->"data")
}

# Escapa comillas del contenido de la Raspberry
:set content [:toarray $content]
:local escapedContent ""
:foreach c in=$content do={
    :if ($c = "\"") do={
        :set escapedContent ($escapedContent . "\\\"")
    } else={
        :set escapedContent ($escapedContent . $c)
    }
}

:log info ("[Grid Guardian] Raspberry Data: $escapedContent")
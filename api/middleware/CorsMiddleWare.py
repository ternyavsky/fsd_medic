def open_access_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        # response["Access-Control-Allow-Origin"] = "http://pre-recover.com"
        response["Access-Control-Allow-Origin"] = "http://localhost"
        response["Access-Control-Allow-Headers"] = (
            "Content-Type,Content-Length, Authorization, Accept,X-Requested-With, access-control-allow-methods,access-control-allow-origin, Sessionid"
        )
        response["Access-Control-Allow-Methods"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"

        return response

    return middleware

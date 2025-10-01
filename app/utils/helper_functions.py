
def return_response(response, error=False):
    response["status_code"] = 505 if error else 200
    return response
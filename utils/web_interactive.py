import requests


class WebInteractive:
    @staticmethod
    def clean_req_data(req_data):
        req_data_pop = []

        for k in ['data', 'params']:
            if k in req_data.keys():
                data = req_data.get(k)  # type: dict
                if data is not None:
                    data_pop = []
                    for _k, v in data.items():
                        if v is None:
                            data_pop.append(_k)
                    for i in data_pop:
                        data.pop(i)
                else:
                    req_data_pop.append(k)

        for i in req_data_pop:
            req_data.pop(i)

        return req_data

    @staticmethod
    def request(method: str, url):
        method = method.upper()

        def core(func):
            def _core(*args, **kwargs):
                req_data = func(*args, **kwargs)  # type: dict
                req_data = WebInteractive.clean_req_data(req_data)
                url_args = req_data.get('url_args')
                req_data.pop('url_args')

                if url_args is not None and len(url_args) > 0:
                    req_url = url % url_args
                else:
                    req_url = url

                if method == 'GET':
                    resp = requests.get(req_url, **req_data)
                elif method == 'POST':
                    resp = requests.post(req_url, **req_data)
                else:
                    resp = None

                return resp

            return _core

        return core

    @staticmethod
    def response(attr, encoding=None, params=None):
        def core(func):
            def _core(*args, **kwargs):
                resp = func(*args, **kwargs)  # type: requests.Response
                if resp is not None:
                    if encoding is not None:
                        resp.encoding = encoding
                    result = getattr(resp, attr)
                    if callable(result):
                        if params is not None:
                            result = result(**params)
                        else:
                            result = result()
                else:
                    result = None

                return result

            return _core

        return core

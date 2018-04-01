# -*- encoding: utf-8 -*-
import datetime

def get_params_from_line(line):
    try:
        line = line.split('\"')
        request_date = line[0].strip()
        if request_date[0] != '[' or request_date[-1] == -1:
            return None
        request_date = request_date[1:-1]
        request_date = datetime.datetime.strptime(request_date, '%d/%b/%Y %H:%M:%S')
        _request_type = line[1].split()[0]
        request = line[1].split()[1]
        protocol = line[1].split()[2].split('/')[0]
        protocol_version = line[1].split()[2].split('/')[1]
        response_code = line[2].strip().split()[0]
        response_time = line[2].strip().split()[1]
        protocol_in_url = request[:request.find(':')]
        request = request[len(protocol_in_url) + len(":"):]
        if request[:2] == "//":
            request = request[2:]
        if request.find('@') != -1:
            request = request[request.find('@') + 1:]
        if request.find(':') != -1:
            if request.find('/') != -1:
                request = request[:request.find(':')] + request[request.find('/'):]
            else:
                request = request[:request.find(':')]
        if request.find('?') != -1:
            url = request[:request.find('?')]
        elif request.find('#') != -1:
            url = request[:request.find('#')]
        else:
            url = request
        return request_date, _request_type, url, response_time

    except Exception as e:
        return None

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    urls = dict()
    response_times = dict()
    try:
        with open("log.log", "r") as log_file:
            for line in log_file:
                parsed_params = get_params_from_line(line)
                if parsed_params:
                    request_date, _request_type, url, response_time = parsed_params
                else:
                    continue
                if (start_at and request_date < start_at) or (request_type and _request_type != request_type) or \
                    (ignore_files and '.' in url[url.rfind('/') + 1:]):
                    continue
                if stop_at and request_date > stop_at:
                    break
                if ignore_www and url[:3] == "www":
                    # учитываем, что если www игнорируется, то и в ignore_urls тоже неразличаем.
                    if url in ignore_urls or url[4:] in ignore_urls:
                        continue
                    url = url[4:]
                elif url in ignore_urls:
                    continue

                urls[url] = urls[url] + 1 if url in urls else 1
                if slow_queries:
                    response_times[url] = response_times[url] + int(response_time) if url in response_times else int(response_time)

        return get_results(urls, response_times, slow_queries)
    except IOError as e:
        return []

def get_results(urls, response_times, slow_queries):
    if not slow_queries:
        top_urls = sorted(urls.items(), key=lambda x: x[1], reverse=True)[:5]
        result = [top_url[1] for top_url in top_urls]
    else:
        for url in urls:
                response_times[url] //= int(urls[url])
        top_urls = sorted(response_times.items(), key=lambda x: x[1], reverse=True)[:5]
        result = [top_url[1] for top_url in top_urls]
    return result
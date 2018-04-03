# -*- encoding: utf-8 -*-
import datetime


def get_params_from_line(line):
    line = line.split('\"')
    request_date = line[0].strip()
    if request_date[0] != '[' or request_date[-1] != ']':
        return None
    request_date = request_date[1:-1]
    try:
        request_date = datetime.datetime.strptime(request_date, '%d/%b/%Y %H:%M:%S')
    except ValueError:
        return None
    try:
        str_in_quotes = line[1].strip().split()
        _request_type = str_in_quotes[0]
        request = str_in_quotes[1]
        response_time = line[2].strip().split()[1]
    except IndexError:
        return None

    protocol_in_url = request[:request.find(':')]
    request = request[len(protocol_in_url) + len(":"):]
    if request[:2] == "//":
        request = request[2:]
    if request.find('@') != -1:
        request = request[request.find('@') + 1:]
    
    colon_position = request.find(':')
    if colon_position != -1:
        if request.find('/') != -1:
            request = request[:colon_position] + request[request.find('/'):]
        else:
            request = request[:colon_position]

    question_mark_position = request.find('?')
    grating_mark_position = request.find('#')
    if question_mark_position != -1:
        url = request[:question_mark_position]
    elif grating_mark_position != -1:
        url = request[:grating_mark_position]
    else:
        url = request
        
    return request_date, _request_type, url, response_time


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
                if (start_at and request_date < start_at) or \
                    (request_type and _request_type != request_type) or \
                    (ignore_files and '.' in url[url.rfind('/') + 1:]):
                    continue
                if stop_at and request_date > stop_at:
                    break
                if ignore_www and url[:3] == "www":
                    if url in ignore_urls or url[4:] in ignore_urls:
                        continue
                    url = url[4:]
                elif url in ignore_urls:
                    continue

                urls[url] = urls[url] + 1 if url in urls else 1
                if slow_queries:
                    try:
                        if url in response_times:
                            response_times[url] += int(response_time)
                        else:
                            response_times[url] = int(response_time)
                    except ValueError:
                        continue

        if slow_queries:
            for url in urls:
                response_times[url] //= int(urls[url])

        return get_results((urls, response_times)[slow_queries])

    except IOError:
        return []


def get_results(results_dict):
    top_urls = sorted(results_dict.items(), key=lambda x: x[1], reverse=True)[:5]
    result = [top_url[1] for top_url in top_urls]

    return result
import csv
import functools

import requests


def read_file():
    with open("./mydata2AM/meta_species.txt") as s_f:
        csv_reader = csv.reader(s_f, delimiter=',')
        names = [(row[1], row[3]) for row in csv_reader]

        def search(cname):
            payload = {"q": cname}
            result = requests.get(
                "https://api.gbif.org/v1/species/search",
                params=payload)
            parsed_response = result.json()
            parsed_response["results"].sort(
                key=lambda i: len(
                    i["higherClassificationMap"].values()),
                reverse=True)
            keys = ["results", "0", "higherClassificationMap"]
            cmap = functools.reduce(lambda val, key: val.get(key) if isinstance(val, dict)
                                    else (val[int(key)]
                                          if (isinstance(val, list) and len(val) != 0)else None),
                                    keys, parsed_response)
            return (cname, parsed_response["count"], list(
                cmap.values()) if cmap is not None else None)

        def fallback(fallback_search, result, depth=0):
            (_, _, value) = result
            if depth == 2:
                print("Max Recursion depth reached for {}".format(fallback_search))
                return result
            elif value is None:
                f_result = search(fallback_search)
                return f_result
            elif len(value) <= 1:
                return search(fallback_search)
            else:
                return result
        return [fallback(cname, search(sname))
                for (cname, sname) in names[1:]]


if __name__ == "__main__":
    RESULTS = read_file()
    FOUND_RESULTS = [(name, value)
                     for (name, count, value) in RESULTS if value is not None]
    MISSED_RESULTS = [
        name for (
            name,
            count,
            value) in RESULTS if value is None]
    print("Found:{}".format(len(FOUND_RESULTS)))
    print("Missed:{}\t${}".format(len(MISSED_RESULTS), MISSED_RESULTS))
    print("*****Results*****")
    for (name, _, taxon) in RESULTS:
        print("{}\t{}".format(name, taxon))

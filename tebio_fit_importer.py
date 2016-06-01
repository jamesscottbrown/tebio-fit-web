from bs4 import BeautifulSoup
import json
import sys

def element_to_array(element):
    return str(element.string).replace("  ", " ").strip().split(" ")


def element_to_str(element):
    return str(element.string.strip())


def process_params(model):
    param_data = []
    c = 0
    for param in model.select_one("parameters"):
        if not param.name:
            continue
        tmp = {"name": param.name, "column": c}

        spec = element_to_array(param)
        tmp["type"] = spec[0]
        if spec[0] == "constant":
            tmp["string"] = "Constant(%s)" % (spec[1])
            tmp["min"] = spec[1]
            tmp["max"] = spec[1]

        elif spec[0] == "normal":
            tmp["string"] = "Normal(%s, %s)" % (spec[1], spec[2])
            tmp["min"] = float(spec[1]) - 3 * float(spec[2])
            tmp["max"] = float(spec[1]) + 3 * float(spec[2])

        elif spec[0] == "uniform":
            tmp["string"] = "Uniform(%s, %s)" % (spec[1], spec[2])
            tmp["min"] = spec[1]
            tmp["max"] = spec[2]

        elif spec[0] == "lognormal":
            # TODO: think about whether these axes choices are reasonable
            tmp["string"] = "U(%s, %s)" % (spec[1], spec[2])
            tmp["min"] = float(spec[1]) - 3 * float(spec[2])
            tmp["max"] = float(spec[1]) + 3 * float(spec[2])

        c += 1
        param_data.append(tmp)

    return param_data


def process_models(soup):
    models_data = []
    for model in soup.select_one("models").children:
        if not model.name:
            continue  # skip the 'NavigableString's, and process only the Tags

        model_data = {"model_name": element_to_str(model.select_one("name")),
                      "sbml_name": element_to_str(model.select_one("source")),
                      "fit": element_to_array(model.select_one("fit")),
                      "initial_conditions": []}

        # require constant IC
        for ic in model.select_one("initial"):
            if not ic.name:
                continue
            tmp = {"name": ic.name, "value": str(ic.string.replace('constant', '').strip())}
            model_data["initial_conditions"].append(tmp)

        model_data["params"] = process_params(model)

        models_data.append(model_data)

    return models_data


def process_measurements(soup):
    measurements = []
    for var in soup.select_one("variables").children:
        if not var.name:
            continue  # skip the 'NavigableString's, and process only the Tags
        measurements.append(element_to_array(var))
    return measurements


def process_file(path):
    f = open(path, 'r')
    html_doc1 = f.read()
    soup = BeautifulSoup(html_doc1, 'xml')

    # only handles single epsilon schedule
    data = {"epsilon_schedule": element_to_array(soup.select_one("epsilon").select_one("e1")),
            "particles": element_to_array(soup.select_one("particles")),
            "times": element_to_array(soup.select_one("times")),
            "measurements": process_measurements(soup),
            "models": process_models(soup)}

    print json.dumps(data)


if __name__ == '__main__':
    argv = sys.argv

    if len(argv) == 0:
        print "Must supply path to input file as argument"
    else:
        process_file(argv[1])
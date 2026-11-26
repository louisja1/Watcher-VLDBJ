import io
import csv

def parse_inserted_field(field):
    attr_vals = []
    if '"' in field:
        # there are string attributes (for now in IMDB only)
        reader = csv.reader(io.StringIO(field), quotechar='"', doublequote=True)
        for row in reader:
            for x in row:
                if x == "None" or x == "":
                    attr_vals.append(None)
                else:
                    attr_vals.append(x)
    else:
        for x in field.split(","):
            if x == "None" or x == "":
                attr_vals.append(None)
            else:
                attr_vals.append(x)
    return attr_vals
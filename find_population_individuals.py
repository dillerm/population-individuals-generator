from rdflib import *
import datetime as dt
from csv import DictWriter


# Formats an input species name for the output file name
def format_for_fname(species_name):
    formatted_name = species_name.lower()

    if " " in species_name.lower():
        formatted_name = species_name.lower().replace(" ", "-")

    return formatted_name


obc_hand = input("Path to obc-ide-indexing-instances-and-classes.owl: ")

pathogen_inp = input("Enter species name of pathogen organism(s) that you would like all individuals and their IRIs for: ")
host_inp = input("Enter species name of host organism(s) that you would like all individuals and their IRIs for: ")

g = Graph()
pathogen_graph = g.parse(obc_hand)

list_of_pathogen_dicts = list()
list_of_host_dicts = list()
list_of_population_dicts = list()

for s, p, o in pathogen_graph:
    pathogen_dict = dict()
    host_dict = dict()

    if "NamedIndividual" in o:
        try:
            rdfs_label = g.label(s).toPython()

            if pathogen_inp in rdfs_label:
                if rdfs_label == pathogen_inp : continue

                abbr_iri = g.qname(s).replace(":", "/")
                full_iri = "http://www.pitt.edu/" + abbr_iri

                pathogen_dict[rdfs_label] = full_iri
                list_of_pathogen_dicts.append(pathogen_dict)
            elif host_inp in rdfs_label:
                if rdfs_label == host_inp : continue
                if not " in " in rdfs_label : continue

                abbr_iri = g.qname(s).replace(":", "/")
                full_iri = "http://www.pitt.edu/" + abbr_iri

                host_dict[rdfs_label] = full_iri
                list_of_host_dicts.append(host_dict)
        except : continue

for pathogen in list_of_pathogen_dicts:
    population_dict = dict()
    for p_k,p_v in pathogen.items():

        pathogen_location = p_k.split(" in ")[1]

        for host in list_of_host_dicts:
            for h_k, h_v in host.items():
                if pathogen_location == h_k.split(" in ")[1]:
                    population_dict["host_label"] = h_k
                    population_dict["host_iri"] = h_v
                    population_dict["pathogen_label"] = p_k
                    population_dict["pathogen_iri"] = p_v
                    list_of_population_dicts.append(population_dict)

today = dt.datetime.today().strftime("%Y-%m-%d-T%H-%M")
output_fname = format_for_fname(pathogen_inp) + "-in-" + format_for_fname(host_inp) + "-" + today + ".txt"

with open(output_fname, "a") as output_f:
    fieldnames = ["pathogen_iri", "pathogen_label", "host_iri", "host_label"]

    dict_writer = DictWriter(output_f, fieldnames=fieldnames, delimiter="\t")
    dict_writer.writeheader()

    for populations in list_of_population_dicts:
        dict_writer.writerow(populations)

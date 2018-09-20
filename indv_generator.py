from rdflib import *
import datetime as dt


# Note: rdflib currently has pre-defined namespaces for RDF, XML, RDFS, FOAF, and DC, among other things.
# Defined namespaces
obo = "http://purl.obolibrary.org/obo/"
obc = "http://www.pitt.edu/obc/"

# Necessary IRIs
ecosystem_class_iri = "&obo;APOLLO_SV_00000097"
biotic_ecosystem_class_iri = "&obo;APOLLO_SV_00000104"
population_iri = "http://purl.obolibrary.org/obo/PCO_0000001"
pathogen_population_class_iri = "http://www.pitt.edu/obc/IDE_0000000007"
virus_population_class_iri = "http://www.pitt.edu/obc/IDE_0000000226"
bacteria_population_class_iri = "http://www.pitt.edu/obc/IDE_0000000218"
host_population_class_iri = "http://purl.obolibrary.org/obo/APOLLO_SV_00000516"


if __name__ == "__main__":
    geo_input = input("Enter name(s) of geographical regions (separated by semicolons) or the location of the file ("
                     ".owl or .txt formats only) containing them: ")
    obc_hand = input("Enter path to obc-ide.owl: ")
    starting_iri = input("Enter the numerical portion of the IRI that will be for the first individual created (i.e., "
                         "everything after the 'IDE_': ")

    ecosystems_prompt = input("Do you need to generate ecosystem individuals? [y/n] ")
    bio_ecosystems_prompt = input("Do you need to generate biotic ecosystem individuals? [y/n] ")
    populations_prompt = input("Do you need to generate population individuals? [y/n] ")

    populations_needed, population_iris = list(), list()

    if populations_prompt == "y":
        population_species = input("List the species you'd like to create population individuals for. If there are "
                                   "multiple species, separate each with a semicolon: ")
        population_class_iri = input("""Enter the IRI for the population class(es), excluding the namespace.
        For example, for 'http://www.pitt.edu/obc/IDE_0000000218', only enter 'IDE_0000000218'.
        """)
        species_needed = population_species.split("; ")
        species_iris = "&obc;{}".format(population_class_iri.split("; "))

        for species in species_needed:
            populations_needed.append(species)
        for iri in species_iris:
            population_iris.append(iri)

    iri_count = int(starting_iri)

    geo_individuals = dict() # For .owl file input only
    locations = set() # For .txt file input only

    new_ecosystem_region = dict()
    uninhabited_regions = [
        "Stoltenhoff Island",
        "Middle Island",
        "Nightingale Island",
        "Nightingale Islands",
        "Inaccessible Island",
        "Gough Island"
    ]
    new_ecosystem_indvs = list()
    new_biotic_ecosystem_indvs = list()
    new_species_indvs = list()

    # Pull out regions from file
    if ".owl" in geo_input:
        g1 = Graph()
        geo = g1.parse(geo_input)

        if ecosystems_prompt == "y":
            for s, p, o in geo:
                if "NamedIndividual" in o:
                    try:
                        rdflib_label = g1.label(s).toPython()
                        iri = g1.qname(s)

                        rdfs_label = rdflib_label.split("region of ")
                        rdfs_label.reverse()

                        if rdfs_label[0] not in uninhabited_regions:
                            geo_individuals[rdfs_label[0]] = iri

                    except Exception : continue

            ecosystem_regions_in_obc = list()

            g2 = Graph()
            ide = g2.parse(obc_hand)

            # Check for ecosystem individuals
            for s, p, o in ide:
                if "NamedIndividual" in o:
                    try:
                        rdflib_label = g2.label(s).toPython()

                        if "ecosystem of" in rdflib_label:
                            rdfs_label = rdflib_label.split("ecosystem of ")
                            rdfs_label.reverse()

                            ecosystem_regions_in_obc.append(rdfs_label[0])


                    except Exception : continue

            for key,value in geo_individuals.items():
                if key not in ecosystem_regions_in_obc:
                    new_ecosystem_region[key] = value

            # Generate ecosystem and biotic ecosystem individuals for each country in the world
            for region, iri in list(new_ecosystem_region.items()):
                eco_dict = dict()
                biotic_eco_dict = dict()

                eco_dict["label"] = "ecosystem of " + region
                eco_dict["preferredTerm"] = "ecosystem of region of " + region
                eco_dict["location"] = iri
                eco_dict["iri"] = "IDE_000000" + str(iri_count)
                eco_dict["type"] = ecosystem_class_iri

                new_ecosystem_indvs.append(eco_dict)
                iri_count += 1

                part_of = eco_dict.get("iri")

                biotic_eco_dict["label"] = "biotic ecosystem of " + region
                biotic_eco_dict["preferredTerm"] = "biotic ecosystem of region of " + region
                biotic_eco_dict["partOf"] = part_of
                biotic_eco_dict["iri"] = "IDE_000000" + str(iri_count)
                biotic_eco_dict["type"] = biotic_ecosystem_class_iri

                new_biotic_ecosystem_indvs.append(biotic_eco_dict)
                iri_count += 1

                if populations_needed:
                    for population in populations_needed:
                        species_dict = dict()
                        i = populations_needed.index(population)

                        species_dict["type"] = population_iris[i]
                        species_dict["preferredTerm"] = "human population in region of " + region
                        species_dict["label"] = population + " in " + region
                        species_dict["partOf"] = biotic_eco_dict.get("iri")
                        species_dict["iri"] = "IDE_000000" + str(iri_count)

                        new_species_indvs.append(species_dict)
                        iri_count += 1

    elif ".txt" in geo_input:
        with open(geo_input) as f:
            for line in f:
                line = line.rstrip()

                # Normalize country names to the labels used in GEO.
                if line == "United States of America" \
                        or line == "US" \
                        or line == "USA":
                    locations.add("United States")
                elif line == "Venezuela (Bolivarian Republic of)" \
                        or line == "Bolivarian Republic of Venezuela" \
                        or line == "Republic of Venezuela":
                    locations.add("Venezuela")
                elif line == "Bolivia" or line == "Plurinational State of Bolivia":
                    locations.add("Bolivia (Plurinational State of)")
                elif line == "Cape Verde" \
                        or line == "Republic of Cabo Verde" \
                        or line == "Republic of Cape Verde":
                    locations.add("Cabo Verde")
                elif line == "Hawaii":
                    locations.add("Hawai\"i")
                elif line == "Reunion":
                    locations.add("Réunion")
                elif line == "Cocos Islands" or line == "Keeling Islands":
                    locations.add("Cocos (Keeling) Islands")
                elif line == "Laos" or line == "Muang Lao":
                    locations.add("Lao People's Democratic Republic")
                elif line == "Vietnam" or line == "Socialist Republic of Vietnam":
                    locations.add("Viet Nam")
                elif line == "Iran" \
                        or line == "Persia" \
                        or line == "Islamic Republic of Iran":
                    locations.add("Iran (Islamic Republic of)")
                elif line == "UAE" or line == "Emirates":
                    locations.add("United Arab Emirates")
                elif line == "Ivory Coast" or line == "Republic of Côte d'Ivoire":
                    locations.add("Côte d'Ivoire")
                elif line == "United Republic of Tanzania":
                    locations.add("Tanzania")
                elif line == "Curacao":
                    locations.add("Curaçao")
                elif line == "North Korea":
                    locations.add("Democratic People's Republic of Korea")
                elif line == "South Korea":
                    locations.add("Republic of Korea")
                elif line == "Democratic People's Republic of the Congo" \
                        or line == "DRC" \
                        or line == "Zaire" \
                        or line == "DR Congo" \
                        or line == "DROC" \
                        or line == "East Congo" \
                        or line == "Congo-Kinshasa" \
                        or line == "the Congo" or line == "Congo":
                    locations.add("Democratic People's Republic of Congo")
                elif line == "Falkland Islands":
                    locations.add("Falkland Islands (Malvinas)")
                elif line == "Lanai" or line == "Lana'i":
                    locations.add("Lānaʻi")
                elif line == "Micronesia" \
                        or line == "Federated States of Micronesia" \
                        or line == "FSM":
                    locations.add("Micronesia (Federated States of)")
                elif line == "Molokai":
                    locations.add("Molokaʻi")
                elif line == "Niihau":
                    locations.add("Niʻihau")
                elif line == "Oahu":
                    locations.add("Oʻahu")
                elif line == "Abkhazia" or line == "Autonomous Republic of Abkhazia":
                    locations.add("Republic of Abkhazia")
                elif line == "Republic of the Congo" \
                        or line == "Congo-Brazzaville" \
                        or line == "West Congo" \
                        or line == "Congo Republic":
                    locations.add("Republic of Congo")
                elif line == "Kosovo":
                    locations.add("Republic of Kosovo")
                elif line == "Moldova":
                    locations.add("Republic of Moldova")
                elif line == "South Ossetia":
                    locations.add("Republic of South Ossetia")
                elif line == "Russia":
                    locations.add("Russian Federation")
                elif line == "Saint-Barthelemy" \
                        or line == "Saint Barthelemy" \
                        or line == "Saint Barthélemy" \
                        or line == "Territorial collectivity of Saint-Barthélemy":
                    locations.add("Saint-Barthélemy")
                elif line == "Saint Martin" \
                        or line == "Saint-Martin (French)" \
                        or line == "Saint Martin (French)" \
                        or line == "Saint Martin (French Part)":
                    locations.add("Saint-Martin (French part)")
                elif line == "Palestine":
                    locations.add("State of Palestine")
                elif line == "Syria":
                    locations.add("Syrian Arab Republic")
                elif line == "Macedonia" or line == "Republic of Macedonia":
                    locations.add("The former Yugoslav Republic of Macedonia")
                elif line == "United Kingdom" \
                        or line == "UK" \
                        or line == "Great Britain" \
                        or line == "Britain":
                    locations.add("United Kingdom of Great Britain and Northern Ireland")
                elif line == "US Virgin Islands" \
                        or line == "United States Virgin Islands" \
                        or line == "American Virgin Islands":
                    locations.add("Virgin Islands of the United States")
                elif line == "Åland" \
                        or line == "Aland" \
                        or line == "Aland Islands":
                    locations.add("Åland Islands")
                elif line == "Sint Marten":
                    locations.add("Sint Maarten")
                else:
                    locations.add(line)

        g = Graph()
        ide = g.parse(obc_hand)

        for s, p, o in ide:
            if "NamedIndividual" in o:
                try:
                    rdflib_label = g.label(s).toPython()

                    if "biotic ecosystem of" in rdflib_label:
                        if "abiotic" in rdflib_label : continue

                        rdfs_label = rdflib_label.split("ecosystem of ")
                        rdfs_label.reverse()
                        region = rdfs_label[0]

                        if region in locations:
                            for population in populations_needed:
                                pop_dict = dict()

                                ecosystem_iri = g.qname(s)
                                i = populations_needed.index(population)


                                pop_dict["type"] = population_iris[i]
                                pop_dict["preferredTerm"] = "human population in region of " + region
                                pop_dict["label"] = population + " in " + region
                                pop_dict["partOf"] = ecosystem_iri.replace(":", ";")
                                pop_dict["iri"] = "IDE_000000" + str(iri_count)

                                new_species_indvs.append(pop_dict)
                                iri_count += 1
                        else:
                            print(region, " not found in GEO.")
                except Exception : continue

    else:
        if ";" in geo_input:
            geo_regions = geo_input.split("; ")
            for region in geo_regions:
                locations.add(region)
        else:
            locations.add(geo_input)

        g = Graph()
        ide = g.parse(obc_hand)

        population_iri_generators = list()

        # Grab the IRIs for population classes
        pop_classes = g.transitive_subjects(predicate=RDFS.subClassOf, object=URIRef(population_class_iri))
        population_iri_generators.append(pop_classes)

        # Grab the IRIs for host population classes
        host_pop_classes = g.transitive_subjects(predicate=RDFS.subClassOf, object=URIRef(host_population_class_iri))
        population_iri_generators.append(host_pop_classes)

        # Grab the IRIs for virus population classes
        virus_pop_classes = g.transitive_subjects(predicate=RDFS.subClassOf, object=URIRef(virus_population_class_iri))
        population_iri_generators.append(virus_pop_classes)

        # Grab the IRIs for bacteria population classes
        bacteria_pop_classes = g.transitive_subjects(predicate=RDFS.subClassOf, object=URIRef(bacteria_population_class_iri))
        population_iri_generators.append(bacteria_pop_classes)

        # Grab the IRIs for pathogen population classes
        pathogen_pop_classes = g.transitive_subjects(predicate=RDFS.subClassOf, object=URIRef(pathogen_population_class_iri))
        population_iri_generators.append(pathogen_pop_classes)

        population_iris = set()

        for generator in population_iri_generators:
            for iri in generator:
                population_iris.add(iri)

        already_found_iri = list()
        already_found_label = list()

        for s, p, o in ide:
            if "NamedIndividual" in o:
                try:
                    rdflib_label = g.label(s).toPython()
                    iri = g.qname(s)

                    if "biotic ecosystem of" in rdflib_label:
                        if "abiotic" in rdflib_label : continue

                        rdfs_label = rdflib_label.split("ecosystem of ")
                        rdfs_label.reverse()
                        region = rdfs_label[0]

                        if region in locations:
                            new_ecosystem_region[region] = iri
                except Exception : continue

            if s in already_found_iri : continue

            if s in population_iris:
                try:
                    population_label = g.label(s).toPython()

                    if population_label in populations_needed:
                        for key, value in new_ecosystem_region.items():
                            pop_dict = dict()

                            pop_dict["iri"] = "IDE_000000" + str(iri_count)
                            pop_dict["label"] = population_label + " in " + key
                            pop_dict["partOf"] = value.replace(":", ";")
                            pop_dict["type"] = s.toPython()
                            pop_dict["preferredTerm"] = population_label + " population in region of " + key

                            already_found_iri.append(s)
                            new_species_indvs.append(pop_dict)
                            iri_count += 1
                except Exception : continue

    today = dt.datetime.today().strftime("%Y_%m_%d_T%H_%M")

    if ecosystems_prompt == "y":
        ecosystem_output_directory = "population-individuals-output/"
        ecosystem_output_fname = "dependency_ecosystem_individuals_{}.txt".format(today)
        ecosystem_output_location = ecosystem_output_directory + ecosystem_output_fname

        with open(ecosystem_output_location, "a") as ind_f:
            for dct in new_ecosystem_indvs:
                iri = dct.get("iri")
                type = dct.get("type")
                label = dct.get("label")
                pref_term = dct.get("preferredTerm")
                location = dct.get("location").replace(":", ";")

                ind_f.write(
                    "\t" + "<!-- " + obc + iri + " -->" + "\n" + "\n"
                    "\t" + "<owl:NamedIndividual rdf:about=\"&obc;" +  iri + "\">" + "\n"
                    "\t" + "\t" + "<rdf:type rdf:resource="" + type + ""/>" + "\n"
                    "\t" + "\t" + "<rdfs:label xml:lang=\"en\">" + label + "</rdfs:label>" + "\n"
                    "\t" + "\t" + "<obo:IAO_0000111 xml:lang=\"en\">" + pref_term + "</obo:IAO_0000111>" + "\n"
                    "\t" + "\t" + "<ro:located_in rdf:resource=\"&" + location + "\"/>" + "\n"
                    "\t" + "</owl:NamedIndividual>" + "\n" + "\n" + "\n" + "\n"
                )

        biotic_ecosystem_output_directory = "population-individuals-output/"
        biotic_ecosystem_output_fname = "dependency_biotic_ecosystem_individuals_{}.txt".format(today)
        biotic_ecosystem_output_location = biotic_ecosystem_output_directory + biotic_ecosystem_output_fname

        with open(biotic_ecosystem_output_location, "a") as ind_f:
             for dct in new_biotic_ecosystem_indvs:
                    iri = dct.get("iri")
                    type = dct.get("type")
                    label = dct.get("label")
                    pref_term = dct.get("preferredTerm")
                    partOf = dct.get("partOf").replace(":", ";")

                    ind_f.write(
                        "\t" + "<!-- " + obc + iri + " -->" + "\n" + "\n"
                        "\t" + "<owl:NamedIndividual rdf:about=\"&obc;" +  iri + "\">" + "\n"
                        "\t" + "\t" + "<rdf:type rdf:resource=\"" + type + "\"/>" + "\n"
                        "\t" + "\t" + "<rdfs:label xml:lang=\"en\">" + label + "</rdfs:label>" + "\n"
                        "\t" + "\t" + "<obo:IAO_0000111 xml:lang=\"en\">" + pref_term + "</obo:IAO_0000111>" + "\n"
                        "\t" + "\t" + "<obo:BFO_0000137 rdf:resource=\"&obc;" + partOf + "\"/>" + "\n"
                        "\t" + "</owl:NamedIndividual>" + "\n" + "\n" + "\n" + "\n"
                    )

    if populations_prompt == "y":
        populations_output_directory = "population-individuals-output/"
        populations_output_fname = "population_individuals_{}.txt".format(today)
        populations_output_location = populations_output_directory + populations_output_fname

        with open(populations_output_location, "a") as ind_f:
             for dct in new_species_indvs:
                 iri = dct.get("iri")
                 type = dct.get("type")
                 label = dct.get("label")
                 pref_term = dct.get("preferredTerm")
                 partOf = dct.get("partOf").replace(":", ";")

                 ind_f.write(
                     "\t" + "<!-- " + obc + iri + " -->" + "\n" + "\n"
                     "\t" + "<owl:NamedIndividual rdf:about=\"&obc;" +  iri + "\">" + "\n"
                     "\t" + "\t" + "<rdf:type rdf:resource=\"" + type + "\"/>" + "\n"
                     "\t" + "\t" + "<rdfs:label xml:lang=\"en\">" + label + "</rdfs:label>" + "\n"
                     "\t" + "\t" + "<obo:IAO_0000111 xml:lang=\"en\">" + pref_term + "</obo:IAO_0000111>" + "\n"
                     "\t" + "\t" + "<obo:BFO_0000137 rdf:resource=\"&" + partOf + "\"/>" + "\n"
                     "\t" + "</owl:NamedIndividual>" + "\n" + "\n" + "\n" + "\n"
                )
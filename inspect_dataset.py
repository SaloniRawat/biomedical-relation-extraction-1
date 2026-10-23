print("My first research project")

from zipfile import ZipFile 
archive_path = "data/raw/CDR_Data.zip"

training_file=(
    "CDR_Data/CDR.Corpus.v010516/"
    "CDR_TrainingSet.PubTator.txt"
)
with ZipFile(archive_path) as archive: 
   # for name in archive.namelist():
    #    print(name)
    text = archive.read(training_file).decode("utf-8")

articles = text.strip().split("\n\n")
first_article = articles[0]


for line in first_article.splitlines():
    if "|t|" in line:
        article_id, title = line.split("|t|", 1)
        print("TITLE:", title)

    elif "|a|" in line:
        article_id, abstract = line.split("|a|", 1)
        print("ABSTRACT:", abstract)

    else:
        fields = line.split("\t")

        if len(fields) == 4 and fields[1] == "CID":
            print("RELATION:", fields[2], "->", fields[3])

        elif len(fields) >= 6:
            print("ENTITY:", fields[3], "|", fields[4], "|", fields[5])
article_count = 0
chemical_mentions = 0
disease_mentions = 0
relation_count = 0

for article in articles:
    if not article.strip():
        continue

    article_count += 1

    for line in article.splitlines():
        fields = line.split("\t")

        if len(fields) == 4 and fields[1] == "CID":
            relation_count += 1

        elif len(fields) >= 6:
            if fields[4] == "Chemical":
                chemical_mentions += 1
            elif fields[4] == "Disease":
                disease_mentions += 1

print("\nTRAINING SET SUMMARY")
print("Articles:", article_count)
print("Chemical mentions:", chemical_mentions)
print("Disease mentions:", disease_mentions)
print("Labeled relationships:", relation_count)

candidate_pairs = set()
labeled_pairs = set()

for article in articles:
    chemicals = set()
    diseases = set()
    relations = set()

    for line in article.splitlines():
        if "|t|" in line:
            article_id = line.split("|t|", 1)[0]

        fields = line.split("\t")

        if len(fields) == 4 and fields[1] == "CID":
            relations.add((fields[2], fields[3]))

        elif len(fields) >= 6:
            # Some mentions have multiple identifiers.
            identifiers = set(fields[5].split("|")) - {"-1"}

            if fields[4] == "Chemical":
                chemicals.update(identifiers)
            elif fields[4] == "Disease":
                diseases.update(identifiers)

    for chemical in chemicals:
        for disease in diseases:
            candidate_pairs.add((article_id, chemical, disease))

    for chemical, disease in relations:
        labeled_pairs.add((article_id, chemical, disease))

print("\nPAIR CHECK")
print("Candidate pairs:", len(candidate_pairs))
print("Unique labeled pairs:", len(labeled_pairs))
print("Labeled pairs missing from candidates:",
      len(labeled_pairs - candidate_pairs))

true_positives = len(candidate_pairs & labeled_pairs)
false_positives = len(candidate_pairs - labeled_pairs)
false_negatives = len(labeled_pairs - candidate_pairs)

precision = true_positives / len(candidate_pairs)
recall = true_positives / len(labeled_pairs)
f1 = 2 * precision * recall / (precision + recall)

print("\nALL-PAIRS BASELINE — TRAINING")
print("True positives:", true_positives)
print("False positives:", false_positives)
print("False negatives:", false_negatives)
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")
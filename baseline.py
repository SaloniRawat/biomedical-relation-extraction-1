from zipfile import ZipFile

archive_path = "data/raw/CDR_Data.zip"

training_file = (
    "CDR_Data/CDR.Corpus.v010516/"
    "CDR_TrainingSet.PubTator.txt"
)

with ZipFile(archive_path) as archive:
    text = archive.read(training_file).decode("utf-8")

    articles = text.strip().split("\n\n")

print("Training articles:", len(articles))

candidate_pairs = set()
labeled_pairs = set()

for article in articles:
    chemicals = set()
    diseases = set()
    relations = set()

    for line in article.splitlines():
        if "|t|" in line:
            article_id = line.split("|t|", 1)[0]
           # print ("Reading article:" , article_id)
        
        fields = line.split("\t")

        if len(fields) == 4 and fields[1] == "CID":
            relations.add((fields[2], fields[3]))

        elif len(fields) >= 6:
            identifiers = set(fields[5].split("|")) - {"-1"}

            if fields[4] == "Chemical":
                chemicals.update(identifiers)
            elif fields[4] == "Disease":
                diseases.update(identifiers)
            # Finished reading this article: now build its pairs.
    for chemical in chemicals:
        for disease in diseases:
            candidate_pairs.add((article_id, chemical, disease))

    for chemical, disease in relations:
        labeled_pairs.add((article_id, chemical, disease))

print("Candidate pairs:", len(candidate_pairs))
print("Labeled pairs:", len(labeled_pairs))
print("Missing labeled pairs:", len(labeled_pairs - candidate_pairs))

                
true_positives = len(candidate_pairs & labeled_pairs)
false_positives = len(candidate_pairs - labeled_pairs)
false_negatives = len(labeled_pairs - candidate_pairs)

print("True positives:", true_positives)
print("False positives:", false_positives)
print("False negatives:", false_negatives)

precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)
f1 = 2 * precision * recall / (precision + recall)

print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")

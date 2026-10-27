from zipfile import ZipFile
import re #Python’s built-in tool for matching text patterns

archive_path = "data/raw/CDR_Data.zip"

#training_file = (
#    "CDR_Data/CDR.Corpus.v010516/"
#    "CDR_TrainingSet.PubTator.txt"
#)

# V2: updating with training data
dataset_file = (
    "CDR_Data/CDR.Corpus.v010516/"
    "CDR_DevelopmentSet.PubTator.txt"
)


with ZipFile(archive_path) as archive:
    text = archive.read(dataset_file).decode("utf-8")

    articles = text.strip().split("\n\n")

print("Development articles:", len(articles))

candidate_pairs = set()
labeled_pairs = set()
same_sentence_pairs = set()

for article in articles:
    chemicals = set()
    diseases = set()
    relations = set()
    mentions = []
    

    for line in article.splitlines():
        if "|t|" in line:
            article_id, title = line.split("|t|", 1)
            #print ("Reading article + title:" , article_id, title)

        elif "|a|" in line:
            _, abstract = line.split("|a|", 1)
        
        fields = line.split("\t")
        #print(fields)

        if len(fields) == 4 and fields[1] == "CID":
            relations.add((fields[2], fields[3]))

        elif len(fields) >= 6:
            identifiers = set(fields[5].split("|")) - {"-1"}

            mentions.append({
                "start": int(fields[1]),
                "end": int(fields[2]),
                "text": fields[3],
                "type": fields[4],
                "ids": identifiers,
            })

            if fields[4] == "Chemical":
                chemicals.update(identifiers)
            elif fields[4] == "Disease":
                diseases.update(identifiers)
    
    article_text = title + " " + abstract
    
    sentence_spans = []

    #records the start and end character positions of each sentence-like chunk. 
    # Keeping positions lets us check which mentions fall inside each chunk.
    for match in re.finditer(r"[^.!?]+(?:[.!?]+|$)", article_text):
        sentence_spans.append((match.start(), match.end()))

    # NEW: collect chemical and disease IDs within each chunk.
    for sentence_start, sentence_end in sentence_spans:
        sentence_chemicals = set()
        sentence_diseases = set()

        for mention in mentions:
            if (
                sentence_start <= mention["start"]
                and mention["end"] <= sentence_end
            ):
                if mention["type"] == "Chemical":
                    sentence_chemicals.update(mention["ids"])
                elif mention["type"] == "Disease":
                    sentence_diseases.update(mention["ids"])
        
        for chemical in sentence_chemicals:
            for disease in sentence_diseases:
                same_sentence_pairs.add((article_id, chemical, disease))

    if article == articles[0]:
        print("\nFIRST ARTICLE — SENTENCE CHUNKS")
        for start, end in sentence_spans:
            print(repr(article_text[start:end]))

    # NEW: check the first five mentions in the first article.
    if article == articles[0]:
        for mention in mentions[:5]:
            start = mention["start"]
            end = mention["end"]
            extracted = article_text[start:end]
            print("Match:", extracted == mention["text"])

    # Finished reading this article: now build its pairs.
    
    for chemical in chemicals:
        for disease in diseases:
            candidate_pairs.add((article_id, chemical, disease))

    for chemical, disease in relations:
        labeled_pairs.add((article_id, chemical, disease))

print("Candidate pairs:", len(candidate_pairs))
print("Labeled pairs:", len(labeled_pairs))
print("Missing labeled pairs:", len(labeled_pairs - candidate_pairs))

print("Same-sentence pairs:", len(same_sentence_pairs))

sentence_tp = len(same_sentence_pairs & labeled_pairs)
sentence_fp = len(same_sentence_pairs - labeled_pairs)
sentence_fn = len(labeled_pairs - same_sentence_pairs)

print("\nSAME-SENTENCE BASELINE")
print("True positives:", sentence_tp)
print("False positives:", sentence_fp)
print("False negatives:", sentence_fn)
                
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

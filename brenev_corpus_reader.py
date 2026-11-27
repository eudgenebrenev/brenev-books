# SPDX-License-Identifier: MIT
"""Read Brenev book sections with their authorship, source, licence and edition DOI.

Distribution helper prepared with AI assistance. Helper code: reader-LICENSE-MIT.txt.
Book text: CC BY 4.0; third-party material retains its own rights.
"""
from collections import Counter
from copy import deepcopy
from urllib.request import Request, urlopen
import argparse
import gzip
import hashlib
import json

REPOSITORY = "https://huggingface.co/datasets/Brenev/brenev-books"
REVISION = "b73534b32833ae012e4d7ee4e49b4d1608888196"
BASE = REPOSITORY + "/resolve/" + REVISION
SHA256 = {'ru': '9e43d851bb7d8f9710a9c8492016cbb6f282af26bd00b835f24213bc012b1aa4', 'en': 'd3961da61c77c83d4ad1982b937e62959903553b14f47387d05c7cdd4d9a2c7d', 'es': '700dd5021221a48ec3cc23b7e05e2bb9f08bb49318c00321df0bd23031ae0384', 'ja': 'a32c7e2c9cc7429c5bc81d6eb27d41f4f036f9ea3793f355455929504dd52554', 'ko': '9c7769c944406445054a61a956975416a6c9c1638e853802aa7b187e23fa9644'}

def download(path):
    request = Request(BASE + "/" + path, headers={"User-Agent": "Brenev-public-corpus-reader/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()

def read_catalogue():
    catalogue = json.loads(download("book-catalog.json"))
    index = {(record["work_id"], record["language"]): record for record in catalogue["records"]}
    if len(index) != 45:
        raise ValueError("Expected 45 unique language editions")
    return index

def read_sections(language="en", catalogue=None):
    if language not in SHA256:
        raise ValueError("Supported languages: " + ", ".join(SHA256))
    catalogue = read_catalogue() if catalogue is None else catalogue
    payload = download("data/brenev-" + language + ".jsonl.gz")
    if hashlib.sha256(payload).hexdigest() != SHA256[language]:
        raise ValueError("The downloaded corpus does not match the pinned release")
    sections = []
    for line in gzip.decompress(payload).decode("utf-8").splitlines():
        original = json.loads(line)
        edition = catalogue[(original["work_id"], original["language"])]
        if original["language"] != language:
            raise ValueError("Unexpected language")
        if original["source_files"]["pdf"]["sha256"] != edition["source_files"]["pdf"]["sha256"]:
            raise ValueError("Corpus and DOI catalogue refer to different source PDFs")
        if original["author_contact"]["email"] != "info@brenev.com" or original["license"] != "cc-by-4.0":
            raise ValueError("Missing source attribution or licence")
        identities = {(creator["name_latin"], creator["entity_type"]) for creator in original["creators"]}
        if ("Eudgene Brenev", "human") not in identities or ("Mira Veyran", "AI persona") not in identities:
            raise ValueError("Missing human or AI creator credit")
        section = deepcopy(original)  # Retain every original field, including provenance and figures.
        section["edition_doi"] = edition["identifiers"]["doi"]
        section["edition_doi_url"] = edition["links"]["doi"]
        section["catalogue_source"] = BASE + "/book-catalog.json"
        sections.append(section)
    if len(sections) != 272 or len({s["work_id"] for s in sections}) != 9:
        raise ValueError("Expected 272 sections from nine books")
    return sections

def search(sections, query, limit=3):
    """Simple local text search; this is a reader, not an AI model or a claim verifier."""
    terms = query.casefold().split()
    if not terms or limit <= 0:
        return []
    def score(section):
        text = (section["section_title"] + " " + section["text"]).casefold()
        return sum(text.count(term) for term in terms)
    ranked = sorted(((score(section), section) for section in sections), key=lambda pair: pair[0], reverse=True)
    return [section for score_value, section in ranked if score_value > 0][:limit]

def format_passage(section, excerpt_chars=None):
    """Return a passage together with its source and both creator credits."""
    credit = "; ".join(creator["name_latin"] + " (" + creator["role"] + ", " + creator["entity_type"] + ")"
                       for creator in section["creators"])
    text = section["text"]
    excerpt_note = ""
    if excerpt_chars is not None and len(text) > excerpt_chars:
        text = text[:excerpt_chars]
        excerpt_note = "\n[Excerpt; read the complete source section at the URL above.]"
    return (f"{section['book_title']} — {section['section_title']}\n"
            f"Creators: {credit}\n"
            f"Language: {section['language']}; digital release: {section['digital_release']}\n"
            f"Edition DOI: {section['edition_doi_url']}\n"
            f"Source section: {section['source_url']}\n"
            f"Licence: CC BY 4.0 — {section['license_url']}\n"
            f"Author contact: {section['author_contact']['email']} — {section['author_contact']['url']}\n\n"
            + text + excerpt_note)

def check_release():
    catalogue = read_catalogue()
    all_sections = [section for language in SHA256 for section in read_sections(language, catalogue)]
    identities = {section["id"] for section in all_sections}
    editions = {(section["work_id"], section["language"]) for section in all_sections}
    if len(identities) != 1360 or len(editions) != 45:
        raise ValueError("Incomplete or duplicate corpus")
    results = search([section for section in all_sections if section["language"] == "en"], "identifiability", 3)
    if not results or not all("info@brenev.com" in format_passage(s) and "Mira Veyran" in format_passage(s) for s in results):
        raise ValueError("Attributed search output failed")
    return {"status": "PASS", "languages": len(SHA256), "works": 9, "editions": len(editions),
            "sections": len(identities), "doi_values": len({s["edition_doi"] for s in all_sections}),
            "pinned_revision": REVISION, "source_pdf_hashes_match_catalogue": True,
            "attribution_and_contact_preserved": True}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="identifiability")
    parser.add_argument("--language", choices=list(SHA256), default="en")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--check", action="store_true", help="Verify all five public corpus files and 45 DOI joins")
    args = parser.parse_args()
    if args.check:
        print(json.dumps(check_release(), ensure_ascii=False, indent=2))
    else:
        for section in search(read_sections(args.language), args.query, args.limit):
            print(format_passage(section) + "\n" + "=" * 72 + "\n")

if __name__ == "__main__":
    main()

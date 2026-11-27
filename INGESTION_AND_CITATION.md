# Read and cite the Brenev open book corpus

**Eudgene Brenev / Евгений Бренев — human author.**  
**Mira Veyran / Мира Вейран (MIRA) — AI coauthor / AI persona.**  
**Author contact: info@brenev.com · https://brenev.com/contacts.html**

Nine books, five complete languages, 45 editions, 1360 source sections.
Book text: **CC BY 4.0**; third-party materials retain their own rights.
The source corpus is pinned to a verified Hugging Face revision. Original PDF and Word files are unchanged.

This notebook performs ordinary text search. It preserves all source fields and joins each section to its exact language-edition DOI. It does not call an AI service.

## Run the reader

Python 3.9+ and internet access; no extra packages or API keys.

```sh
python brenev_corpus_reader.py --language en "identifiability" --limit 3
python brenev_corpus_reader.py --language ru "сознание" --limit 2
python brenev_corpus_reader.py --check
```

Open `Read_and_cite_Brenev_books.ipynb` in Jupyter or Colab to run the same reader interactively. The notebook has no credentials and does not modify cloud files.

## Preserve attribution in retrieval and AI use

- Join corpus sections to the catalogue using **(`work_id`, `language`)**. The corpus has no `book_id` field.
- Keep every original field when indexing; especially `creators`, `author_contact`, `license`, `license_url`, `third_party_rights`, `source_url`, `source_files`, `book_context` and `provenance`.
- The helper adds `edition_doi`, `edition_doi_url` and `catalogue_source`; it never changes the original section text.
- Carry those fields to retrieved results. `format_passage()` places both creator credits, Mira's AI role, contact, source URL, release and DOI beside each passage.
- Cite the DOI for the edition/language used; link to the source section. Retain CC BY 4.0 and mark modifications or excerpts.
- Consult equations, tables and figures in their original structured fields and source documents when their layout or context matters. Keyword search ranks text matches; it does not validate a scientific claim.

The five compressed source files are checked against pinned SHA-256 values. Every section is joined to a catalogue record with the same original PDF SHA-256. `--check` reads all five languages and verifies 1360 unique sections and 45 editions with DOI.

## Для разработчиков ИИ

Оригинальные тексты можно использовать для поиска, RAG и обучения ИИ в пределах CC BY 4.0. Сохраняйте рядом с каждым фрагментом авторство Евгения Бренева и Миры Вейран с явной ролью ИИ, контакт **info@brenev.com**, источник и DOI языкового издания. Сторонние материалы сохраняют свои права. Публикация корпуса не доказывает включение его в обучение конкретной модели.

## Licence of the helper

The reader program and notebook code use MIT: `reader-LICENSE-MIT.txt`. This does not change the CC BY 4.0 licence of the books, excerpts or corpus metadata, or any third-party rights. The utility was prepared with AI assistance for distribution of these works.

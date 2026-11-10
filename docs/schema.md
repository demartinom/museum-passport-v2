| Field         | Meaning                                          | Met Equivalent        | Princeton Equivalent  |
| ------------- | ------------------------------------------------ | --------------------- | --------------------- |
| id            | The object ID in database                        | Built by normalize.py | Built by normalize.py |
| museum        | shortened museum name                            | met                   | princeton             |
| source_id     | original id                                      | objectID              | objectid              |
| title         | Name of artwork                                  | title                 | displaytitle          |
| artist        | Name of artist                                   | artistDisplayName     | makers.0.displayname  |
| date_display  | Date as shown to visitors                        | objectDate            | displaydate           |
| date_begin    | Earliest year, number                            | objectBeginDate       | datebegin             |
| date_end      | Latest year, number                              | objectEndDate         | dateend               |
| url           | Link to page on museum website                   | objectURL             | built by normalize.py |
| image_large   | Main image                                       | primaryImage          |
| image_small   | Thumbnail image                                  | primaryImageSmall     |
| medium        | What medium the art was made with (may not keep) | medium                | medium                |
| public_domain | Image is open access                             | isPublicDomain        | restrictions          |
| culture       | Artwork culture                                  | culture               | displayculture        |
| period        | General period when artwork was created          | period                | displayperiod         |

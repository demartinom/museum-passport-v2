| Field            | Meaning                                                       | Met Equivalent                 | Princeton Equivalent            |
| ---------------- | ------------------------------------------------------------- | ------------------------------ | ------------------------------- |
| id               | The object ID in database                                     | Built by normalize.py          | Built by normalize.py           |
| museum           | shortened museum name                                         | met                            | princeton                       |
| museum_full_name | Full name of museum                                           | The Metropolitan Museum of Art | Princeton University Art Museum |
| source_id        | original id                                                   | objectID                       | objectid                        |
| title            | Name of artwork                                               | title                          | displaytitle                    |
| artist           | Name of artist                                                | artistDisplayName              | makers.0.displayname            |
| date_display     | Date as shown to visitors                                     | objectDate                     | displaydate                     |
| date_begin       | Earliest year. Negative = BCE. Null = unknown. See Date rules | objectBeginDate                | datebegin                       |
| date_end         | Latest year. Negative = BCE. Null = unknown. See Date rules   | objectEndDate                  | dateend                         |
| url              | Link to page on museum website                                | objectURL                      | built by normalize.py           |
| image_large      | Main image                                                    | primaryImage                   | built by normalize.py           |
| image_small      | Thumbnail image                                               | primaryImageSmall              | built by normalize.py           |
| image_base       | Base url for IIIF                                             | none                           | primaryimage.0                  |
| medium           | What medium the art was made with (may not keep)              | medium                         | medium                          |
| public_domain    | Image is open access                                          | isPublicDomain                 | restrictions                    |
| culture          | Artwork culture                                               | culture                        | displayculture (open question)  |
| period           | General period when artwork was created                       | period                         | displayperiod                   |

## Date rules

Both museums use `0` as a placeholder for a missing year. There is no year 0 in the calendar (1 BCE is followed by 1 CE), so a `0` is never a real date.

| Source (begin / end) | Stored as   | Why                                                                                                      |
| -------------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| 0 / 0                | null / null | No date information at all. Null never matches a date search, so these objects stay out of date results. |
| 0 / 1914             | 1914 / 1914 | Only the end year is known ("made by 1914"). Copying it keeps the object findable in date searches.      |

Without this rule, a `0` start year made a 1914 object look like it spanned years 0–1914, so it matched searches like 1000–1200 and sorted to the top of the results.

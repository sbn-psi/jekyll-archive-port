# PDS Web Viewer Solr Options

Our web application needs to be able to fetch information about multiple datasets and context objects in any number of queries. A target needs to know which missions have visited it, a mission needs to know which instruments it has, an instrument needs to know which datasets it was used for, and each dataset needs to know about its instrument, target, mission, and other related datasets. 

The typical use-case for Solr is to search for entities based on some number of fields, and to return a list of documents that match, in some sorted or filtered way. This, unfortunately, is not how we will be using Solr. We simply need to lookup specific objects by some ID, and then also look up all related objects based on that object’s relationships. It more closely represents a Graph database or RDB.

## Scenario 1: Each entity gets its own collection
Label-harvested data goes into pds, Dataset metadata goes into web-ui, Targets into targets, etc.

### Example: 
```
web-ui: 
{
    ...
    "display_name": "OSIRIS-REx OCAMS Bundle",
    "download_url": "https://sbnarchive.psi.edu/pds4/orex/orex.ocams.zip",
    "mission_bundle": "urn:nasa:pds:orex.mission",
    "mission": "OSIRIS-REx",
    "targets": ["(101955) Bennu"],
    "instruments: ["urn:nasa:pds:context:instrument:ocams.orex"],
    "related_datasets": ["urn:nasa:pds:orex.tagcams",       
        "urn:nasa:pds:orex.ovirs", 
        "urn:nasa:pds:orex.otes"],
    "collections": ["urn:nasa:pds:orex.ocams:document",
        "urn:nasa:pds:orex.ocams:calibration",
        "urn:nasa:pds:orex.ocams:data_raw",
        "urn:nasa:pds:orex.ocams:data_reduced",
        "urn:nasa:pds:orex.ocams:data_calibrated",
        "urn:nasa:pds:orex.ocams:data_hkl0",
        "urn:nasa:pds:orex.ocams:data_hkl1",
        "urn:nasa:pds:orex.ocams:data_eng",
    ]
    ...
}
targets:
{
    "id":"(101955) Bennu",
    "major":true,
    "icon":"/images/bennu.jpg",
    "description":"...",
    "missions":["OSIRIS-REx"],
    "tags":["NEO",
        "PHA",
        "Apollo"]
    ...
}
missions:
{
    "id":"OSIRIS-REx",
    "tags": ["Orbiter"],
    "targets": ["(101955) Bennu"],
    "instruments": [
        "urn:nasa:pds:context:instrument:ocams.orex",
        "urn:nasa:pds:context:instrument:tagcams.orex",
        "urn:nasa:pds:context:instrument:ovirs.orex",
        "urn:nasa:pds:context:instrument:otes.orex",
        "urn:nasa:pds:context:instrument:rexis.orex",
        "urn:nasa:pds:context:instrument:ola.orex",
    ]
    ...
}
instruments:
{
    "id": "urn:nasa:pds:context:instrument:ocams.orex",
    "name": "The OSIRIS-REx Camera Suite Suite (OCAMS) aboard the OSIRIS-REx spacecraft",
    "tags": ["Imager"],
    "mission": "OSIRIS-REx",
    ...
}
tags: 
[
   {
        "id": "asteroid",
        "displayName": "Asteroid",
        "type": "target",
        "parent": null
    },
    {
        "id": "NEO",
        "displayName": "Near-Earth Object",
        "type": "target",
        "parent": "asteroid"
    },
    {
        "id": "PHA",
        "displayName": "Potentially Hazardous Object",
        "type": "target",
        "parent": "asteroid"
    },
    ...
]
```

### Consequences: 
Multiple sequential queries will need to be performed. Because Solr seems to lack the capability of “joining” across collections and returning data about all related entities at the same time, the only alternative seems to be that the primary entity would need to be queried, and then a query for each type of relationship that entity has to another entity.

Sequential queries causes exponential reliance on network/server bandwidth and performance

## Scenario 2: Bi-directional relationships
It may be possible to adjust how we think of these relationships so that we can make things more Solr-friendly. I'd like help in determining how feasible this is:

Each document will keep track of each other document that it's related to, by any ID that it might be looked up by. 
### Example:
```
{
    ...
    "id": "urn:nasa:pds:orex.ocams",
    "display_name": "OSIRIS-REx OCAMS Bundle",
    "download_url": "https://sbnarchive.psi.edu/pds4/orex/orex.ocams.zip",
    "mission_bundle": "urn:nasa:pds:orex.mission",
    "mission": "OSIRIS-REx",
    "targets": ["(101955) Bennu"],
    "instruments: ["urn:nasa:pds:context:instrument:ocams.orex"],
    ...
}
targets:
{
    "id":"(101955) Bennu",
    "major":true,
    "icon":"/images/bennu.jpg",
    "description":"...",
    "missions":["OSIRIS-REx"],
    "datasets":["urn:nasa:pds:orex.ocams",        
        "urn:nasa:pds:orex.tagcams",       
        "urn:nasa:pds:orex.ovirs", 
        "urn:nasa:pds:orex.otes"]
    ...
}
missions:
{
    "id":"OSIRIS-REx",
    "tags": ["Orbiter"],
    "targets": ["(101955) Bennu"],
    "instruments": [
        "urn:nasa:pds:context:instrument:ocams.orex",
        "urn:nasa:pds:context:instrument:tagcams.orex",
        "urn:nasa:pds:context:instrument:ovirs.orex",
        "urn:nasa:pds:context:instrument:otes.orex",
        "urn:nasa:pds:context:instrument:rexis.orex",
        "urn:nasa:pds:context:instrument:ola.orex",
    ],
    "datasets":["urn:nasa:pds:orex.ocams",        
        "urn:nasa:pds:orex.tagcams",       
        "urn:nasa:pds:orex.ovirs", 
        "urn:nasa:pds:orex.otes"]
    ...
}
instruments:
{
    "id": "urn:nasa:pds:context:instrument:ocams.orex",
    "name": "The OSIRIS-REx Camera Suite Suite (OCAMS) aboard the OSIRIS-REx spacecraft",
    "tags": ["Imager"],
    "mission": "OSIRIS-REx",,
    "datasets":["urn:nasa:pds:orex.ocams"]
    ...
}
```
### Consequences:
An example query would then be:
"search for all datasets with lid urn:nasa:pds:orex.ocams, 
    OR all instruments with related datasets urn:nasa:pds:orex.ocams, 
    OR all targets with related datasets urn:nasa:pds:orex.ocams
    OR all missions with related datasets urn:nasa:pds:orex.ocams
    OR all tags with related datasets urn:nasa:pds:orex.ocams
    OR all datasets that are the mission bundle for urn:nasa:pds:orex.ocams,
    OR all datasets that are bundles for urn:nasa:pds:orex.ocams
    OR all datasets that are collections of urn:nasa:pds:orex.ocams
    OR all datasets that are siblings of urn:nasa:pds:orex.ocams"

So, that sucks, but it might be faster than Scenario 1! This would also introduce tremendous bookkeeping, and high amounts of re-indexing. Then the client would still have to stitch data back together, aand there's a lot of risk of corrupted data returning too few or too many documents.

Also, if we ever want to actually search for objects by anything other than what's in that specific document, we'll have all the same problems as Scenario 1


## Scenario 3: “De-normalize” data
Import and flatten out all related data, so that everything is present at query time. We'd need to pre-fetch relationships for each entity and stuff them into one object
### Example:
```
{
    "display_name": "OSIRIS-REx OCAMS Bundle",
    "download_url": "https://sbnarchive.psi.edu/pds4/orex/orex.ocams.zip",
    "mission_bundle_display_name": "urn:nasa:pds:orex.mission",
    "mission_bundle_lid": "urn:nasa:pds:orex.mission",
    ...
    "mission_name":"Origins, Spectral Interpreation, Resource Identification, Security, Regolith Explorer (OSIRIS-REx) Mission",
    "mission_display_name":"OSIRIS-REx",
    "mission_lid":"urn:nasa:pds:context:investigation:mission.orex",
    "mission_tags_display_names": ["Orbiter"],
    "mission_tags_ids": ["Orbiter"],
    "mission_tags_parents_ids": [null],
    "mission_tags_parents_display_names": [null],
    "mission_instruments_lids": [
        "urn:nasa:pds:context:instrument:ocams.orex",
        "urn:nasa:pds:context:instrument:tagcams.orex",
        "urn:nasa:pds:context:instrument:ovirs.orex",
        "urn:nasa:pds:context:instrument:otes.orex",
        "urn:nasa:pds:context:instrument:rexis.orex",
        "urn:nasa:pds:context:instrument:ola.orex",
    ],
    "mission_instruments_display_names": [
        "OSIRIS-REx Camera Suite Suite (OCAMS)",
        "Touch-and-Go Camera Suite (TAGCAMS)",
        "OSIRIS-REx Visible and Near InfraRed Spectrometer (OVIRS)",
        "OSIRIS-REx Thermal Emission Spectrometer (OTES)",
        "Regolith X-Ray Imaging Spectrometer (REXIS)",
        "OSIRIS-REx Laser Altimeter (OLA)",
    ]
    "mission_instruments_primes": [
        true,
        true,
        true,
        true,
        true,
        true,
    ]
    ...
    "targets_lids": ["urn:nasa:pds:context:target:asteroid.101955_bennu"],
    "targets_display_names": ["(101955) Bennu"],
    "targets_ids": ["(101955) Bennu"],
    "targets_tags_ids": ["NEO", 
        "PHA", 
        "Apollo"],
    "targets_tags_display_names": ["Near-Earth Object",
        "Potentially Hazardous Object",
        "Apollo asteroid"],
    "targets_tags_parents_ids": ["asteroid","asteroid","asteroid"],
    "targets_tags_parents_display_names": ["Asteroid","Asteroid","Asteroid"],
    ...
    "instruments_lids: ["urn:nasa:pds:context:instrument:ocams.orex"],
    "instruments_display_names: ["The OSIRIS-REx Camera Suite Suite (OCAMS) aboard the OSIRIS-REx spacecraft"],
    "instruments_tags_display_names": ["Imager"],
    "instruments_tags_ids": ["Imager"],
    "instruments_tags_parent_ids": [null],
    "instruments_tags_parent_display_names": [null],
    ...
    "related_datasets_lids": ["urn:nasa:pds:orex.tagcams",       
        "urn:nasa:pds:orex.ovirs", 
        "urn:nasa:pds:orex.otes"],
    "related_datasets_display_names": ["OSIRIS-REx TAGCAMS Bundle",       
        "OSIRIS-REx OVIRS Bundle", 
        "OSIRIS-REx OTES Bundle"]
    ...
    "collections_lids": ["urn:nasa:pds:orex.ocams:document",
        "urn:nasa:pds:orex.ocams:calibration",
        "urn:nasa:pds:orex.ocams:data_raw",
        "urn:nasa:pds:orex.ocams:data_reduced",
        "urn:nasa:pds:orex.ocams:data_calibrated",
        "urn:nasa:pds:orex.ocams:data_hkl0",
        "urn:nasa:pds:orex.ocams:data_hkl1",
    ],
    "collections_display_names": ["Documents",
        "Calibration file collection",
        "Raw science image data products",
        "Reduced science image data products",
        "Calibrated science image data products",
        "Raw housekeeping data products",
        "Converted housekeeping data products",
    ],
    "collections_download_urls": ["http://example.com",
        "http://example.com",
        "http://example.com",
        "http://example.com",
        "http://example.com",
        "http://example.com",
        "http://example.com",
    ],
    "collections_download_file_names": ["Software Interface Specification",
        "Example File",
        "20160919T162110S802_map_L0sscal_V000.fits",
        "20170922T231714S379_pol_iofL2pan_V017.fits",
        "Example File",
        "Example File",
        "Example File",
    ],
    ...
}
```
### Consequences:
Extreme weight on indexing. Any time any context object, tag, or dataset needs to change, the web interface needs a new field, or a new entry is added with relationships to any other entities, a complete re-index will need to be performed.

Output is difficult to work with, and will need to be re-normalized client-side, causing additional processing time

Vastly greater storage cost, due to duplicated data

Requirement of additional software support to actually store and manage "true" data elsewhere, and perform denormalization
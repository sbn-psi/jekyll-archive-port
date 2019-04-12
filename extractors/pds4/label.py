'''
Common code for label extraction
'''
import os

def extract_collection(collection):
    '''
    Extracts keywords from the Product_Observational element
    '''
    result = {}
    result.update(extract_identification_area(collection.Identification_Area))
    return result

def extract_bundle(bundle):
    '''
    Extracts keywords from the Product_Observational element
    '''
    result = {}
    result.update(extract_identification_area(bundle.Identification_Area))
    result['collections'] = [extract_bundle_member_entry(x) for x in bundle.select("Bundle_Member_Entry")]
    return result

def extract_bundle_member_entry(e):
    result = {}
    if e.lid_reference:
        result['lid'] = e.lid_reference.string
    if e.lidvid_reference:
        result['lidvid'] = e.lid_reference.string
    result['status'] = e.member_status.string
    result['reference_type'] = e.reference_type.string
    return result

def extract_product_observational(product_observational):
    '''
    Extracts keywords from the Product_Observational element
    '''
    result = {}
    result.update(extract_identification_area(product_observational.Identification_Area))
    result.update(extract_file_area(product_observational.File_Area_Observational))
    result.update(extract_observation_area(product_observational.Observation_Area))

    return result

def extract_identification_area(identification_area):
    '''
    Extracts keywords from the Identification_Area element
    '''
    lid = identification_area.logical_identifier.string
    vid = identification_area.version_id.string
    title = identification_area.title.string
    major, minor = [int(x) for x in vid.split(".")]

    result = {
        "logical_id":   lid,
        "collection_id": extract_collection_id(lid),
        "version_id": vid,
        "lidvid": lid + "::" + vid,
        "major": major,
        "minor": minor,
        "title": title
    }

    result.update(extract_citation_information(identification_area.Citation_Information))

    return result

def extract_citation_information(citation_information):
    result = {}
    if citation_information:
        if citation_information.author_list:
            result['author_list'] = citation_information.author_list.string
        if citation_information.editor_list:
            result['editor_list'] = citation_information.author_list.string
        if citation_information.publication_year:
            result['publication_year'] = citation_information.publication_year.string
        if citation_information.description:
            result['description'] = citation_information.description.string

    return result


def extract_observation_area(context_area):
    '''
    Extract from the observation_area element
    '''
    result = extract_time_coordinates(context_area.Time_Coordinates)
    result.update(extract_target_identification(context_area.Target_Identification))

    return result

def extract_time_coordinates(time_coordinates):
    '''
    gets the start and stop time from the time_coordinates element
    '''
    return {
        "start_date": time_coordinates.start_date_time.string,
        "stop_date": time_coordinates.stop_date_time.string
    }

def extract_target_identification(target_identiftcation):
    if target_identiftcation:
        return {
            "target_name": target_identiftcation.select_one('name').string,
            "target_type": [x.string for x in target_identiftcation.select("type")]
        }
    return {}

def extract_file_area(file_area):
    '''
    Extracts keywords from the File_Area element
    '''
    return {
        "file_name": os.path.basename(file_area.File.file_name.string)
    }

def extract_collection_id(lid):
    '''
    Extracts the collection id component from a LID
    '''
    components = lid.split(':')
    if len(components) > 4:
        return lid.split(':')[4]
    return ""


def extract_processing_information(processing_information):
    '''
    Extracts information from the processing area
    '''
    return {'software': [extract_process(process) for process in processing_information.find_all("Process")]}

def extract_process(process):
    '''
    Extract from the process element
    '''
    return extract_software(process.Software)

def extract_software(software):
    '''
    Extract from the software element
    '''
    return {
        "software_id": software.software_id.string,
        "software_version_id": software.software_version_id.string
    }

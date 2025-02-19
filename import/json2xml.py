import json, re
import xml.etree.ElementTree as ET


def json2xml(xml_dict, out_file):

    with open(xml_dict, 'r') as f:
        xml_dict = json.load(f)

    def dict2xml_element(tag, value):
        element = ET.Element(tag)
        if isinstance(value, dict):
            for key, val in value.items():
                if key == "#text":
                    element.text = str(val)
                elif key.startswith('@'):
                    for i in list(val.keys()):
                        element.set(i, val[i])
                else:
                    child_element = dict2xml_element(key, val)
                    element.append(child_element)
        elif isinstance(value, list):
            for item in value:
                element.append(dict2xml_element(tag, item))
        else:
            element.text = str(value)
        return element

    root = ET.Element('doi_batch', xmlns_xsi="http://www.w3.org/2001/XMLSchema-instance", 
                      xsi_schemaLocation="http://www.crossref.org/schema/5.3.0 https://www.crossref.org/schemas/crossref5.3.0.xsd",
                      xmlns="http://www.crossref.org/schema/5.3.0", 
                      xmlns_jats="http://www.ncbi.nlm.nih.gov/JATS1", 
                      xmlns_fr="http://www.crossref.org/fundref.xsd", 
                      xmlns_ai="http://www.crossref.org/AccessIndicators.xsd", 
                      xmlns_mml="http://www.w3.org/1998/Math/MathML", 
                      version="5.3.0")

    helper_dict={"xmlns_xsi":"xmlns:xsi", 
                      "xsi_schemaLocation":"xsi:schemaLocation", 
                      "xmlns_jats":"xmlns:jats", 
                      "xmlns_fr":"xmlns:fr", 
                      "xmlns_ai":"xmlns:ai", 
                      "xmlns_mml":"xmlns:mml"}

    for element in root.iter():
        for attr, value in list(element.attrib.items()):
            for key, replacement in helper_dict.items():
                if key in attr:
                    new_attr = attr.replace(key, replacement)
                    element.set(new_attr, value)
                    del element.attrib[attr]
                    break  

    head_element = dict2xml_element('head', xml_dict['head'])
    root.append(head_element)
    body_element = dict2xml_element('body', xml_dict['body'])
    root.append(body_element)
    tree = ET.ElementTree(root)

    def recursive_remove(element):
        for child in list(element):
            if child.tag.endswith("citation"):  
                element[:] = child[:]  
            else:
                recursive_remove(child) 
    
    recursive_remove(root)
    for el in root.iter():
        match = re.match("^(?:\{.*?\})?(.*)$", el.tag)
        if match:
            el.tag = match.group(1)


    
    tree.write(out_file, encoding="UTF-8", xml_declaration=True)




if __name__ == '__main__':
    input_xml_dict = "xml_dict.json"
    json2xml(input_xml_dict, 'deleteme.xml')
    #j2x("xml_dict.json", 'deleteme.xml')

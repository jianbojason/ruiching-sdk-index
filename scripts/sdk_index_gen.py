
import os
import json
import logging
import sys
def get_json_obj_from_file(file):
    try:
        with open(file, 'r') as f:
            content = f.read()
        return json.loads(content)
    except Exception as e:
        logging.error("json-file-err:"+file +".please fix first")
        logging.error(e)
        sys.exit(1)

def write_json_to_file(json_content, file_name):
        with open(file_name, 'w', encoding='UTF-8') as f:
            f.write(json.dumps(json_content, indent=4))


def walk_all_folder(index_entry_file):
        index_entry = get_json_obj_from_file(index_entry_file)
        if "index" in index_entry:
            index_entry["children"] = list()
            logging.debug("index has index")
            for item in index_entry["index"]:
                abs_path = os.path.abspath(index_entry_file)
                next_entry_file = os.path.join(os.path.dirname(abs_path), item, "index.json")
                sub_index = walk_all_folder(next_entry_file)
                index_entry["children"].append(sub_index)

            index_entry.pop('index')

        return index_entry

def generate_all_index(index_entry_file):
        index_entry = walk_all_folder(index_entry_file)
        #write_json_to_file(index_entry, output_file_name)
        return index_entry


        
import os
import json
import logging
from pathlib import Path

class SdkIndex(object):
    """
    This is the project generator class, it contains the basic parameters and methods in all type of projects
    """

    def __init__(self,
                 sdk_index_root_path):
        self.sdk_index_root_path = Path(sdk_index_root_path)
        if os.name == "nt":
            self.is_in_linux = False
        else:
            self.is_in_linux = True


    def get_url_from_index_file(self, index_file, package_version):
        with open(index_file, "r") as f:
            index_dict = json.loads(f.read())
            all_releases = index_dict["releases"]
            for release in all_releases:
                if release["version"] == package_version:
                    return release["url"]
            return ""



def gen_bsp_sdk_json(bsp_path,workspace):
    parser = bsp_parser.BspParser(bsp_path)
    bsp_json_file = parser.generate_bsp_project_create_json_input(workspace)
    bsp_chip_json_path = os.path.join(bsp_path, "bsp_chips.json")
    try:
        with open(bsp_chip_json_path, "w", encoding="UTF8") as f:
            f.write(str(json.dumps(bsp_json_file, indent=4)))
    except Exception as e:
        logging.error("\nError message : {0}.".format(e))
        exit(1)


if __name__ == "__main__":
    # prg_gen should be @ "/RT-ThreadStudio/plugins/gener/"
    gen_bsp_sdk_json()

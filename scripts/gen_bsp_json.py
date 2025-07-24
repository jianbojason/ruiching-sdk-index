import json
from pathlib import Path

class SdkIndex(object):
    """
    This is the project generator class, it contains the basic parameters and methods in all type of projects
    """

    def __init__(self,
                 sdk_index_root_path):
        self.sdk_index_root_path = Path(sdk_index_root_path)



    def get_url_from_index_file(self, index_file, package_version):
        with open(index_file, "r") as f:
            index_dict = json.loads(f.read())
            all_releases = index_dict["releases"]
            for release in all_releases:
                if release["version"] == package_version:
                    return release["url"]
            return ""





if __name__ == "__main__":
    # prg_gen should be @ "/RT-ThreadStudio/plugins/gener/"
    pass

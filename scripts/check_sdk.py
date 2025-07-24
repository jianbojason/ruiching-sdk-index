
import subprocess
import time
import logging
logging.getLogger().setLevel(logging.INFO)

def execute_command(cmd_string, cwd=None, shell=True):
    sub = subprocess.Popen(cmd_string, cwd=cwd, stdin=subprocess.PIPE,stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, shell=shell, bufsize=4096)
    stdout_str = ''
    while sub.poll() is None:
        err= sub.stderr.read()
        stdout_str += str(sub.stdout.read(), encoding="UTF-8")
        if len(err)>0:
            logging.info(err)
        time.sleep(0.1)
    return stdout_str

logging.info(execute_command("apt-get update && apt-get -y upgrade"))
logging.info(execute_command("python -m pip install --upgrade pip"))
logging.info(execute_command("pip install requests wget pyyaml jsonschema pytest pytest-sugar pytest-html rt-thread-studio"))


import os
import json
import logging
import requests
import sys
from jsonschema import RefResolver, Draft7Validator, FormatChecker
import yaml
from sdk_index_gen import generate_all_index,get_json_obj_from_file
from common_util import clear_dir, do_merge_copy, rename_dir_file,execute_command,download_retry,file_merge_unzip
from ci_config import INDEX_SERVER_URL,CSP_NANO_VERSION,CSP_RTT_VERSION
from gen_csp_json import gen_sdk_para_json_file
from gen_test_case import gen_sdk_test_case
from gen_bsp_json import gen_bsp_sdk_json
def run_id():
    if 'RUN_ID' in os.environ:
        return os.environ['RUN_ID']
    else:
        raise Exception("run_id is null")

def pr_index(prIndex):
    try:
        prid = run_id()
        logging.info("pr_id:"+prid)
        headers={"Content-Type":"application/json; charset=UTF-8"}
        url=INDEX_SERVER_URL+"/pr/"+prid
        response = requests.post(url,data=json.dumps(prIndex),headers=headers,timeout=60)
        if(response.status_code==404):
            raise Exception(response.status_code)
        else:
            logging.info("request-snapshot-Compeleted: {0}.".format(url))
            return json.loads(response.text)
    except Exception as e:
        logging.error("request-snapshot-Failed.")
        logging.error(e)
        sys.exit(1)

def index_schema_check(index_content):
    def get_schema_json_obj(path):
        return get_json_obj_from_file(os.path.join("/rt-thread/sdk-index/scripts/index_schema_check", path))

    index_all_schema = get_schema_json_obj("index_all_schema.json")
    rtt_source_releases_schema = get_schema_json_obj("rtt_source_releases_schema.json")
    csp_schema = get_schema_json_obj("csp_schema.json")
    csp_dvendor_schema = get_schema_json_obj("csp_dvendor_schema.json")
    csp_dvendor_package_schema = get_schema_json_obj("csp_dvendor_package_schema.json")
    csp_dvendor_package_releases_schema = get_schema_json_obj("csp_dvendor_package_releases_schema.json")

    schema_store = {
            index_all_schema['$id']: index_all_schema,
        }

    resolver = RefResolver.from_schema(rtt_source_releases_schema, store=schema_store)
    validator = Draft7Validator(index_all_schema, resolver=resolver, format_checker=FormatChecker())
    validator.validate(index_content)
    logging.info("SDK index checking successful.")


download_dir="/rt-thread/sdk-index/scripts/sdk_check/"
tempdir_folder="/rt-thread/sdk-index/scripts/temp_sdk/"

def init_dir():
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
    if not os.path.exists(tempdir_folder):
        os.mkdir(tempdir_folder)




def check_pkgs():
    list=os.walk(tempdir_folder)
    for path,dirs,files in list:
        for filename in files:
            if os.path.splitext(filename)[1] ==".yaml":
                yaml_file=os.path.join(path,filename)
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content=f.read()
                    map = yaml.load(content,Loader=yaml.FullLoader)
                    if 'pkg_type' in map.keys() and map['pkg_type']=='Board_Support_Packages' and 'yaml_version' in map.keys():
                        os.environ['SDK_CHECK_TYPE'] = 'bsp_check'
                        #skip this bsp
                        logging.info("\n message : {0}. has thirdparty toolchain pkgs dependency. ci skipped".format(filename))
                    else:
                        logging.info("\n message : {0}. yaml_version is not support. ci skipped".format(filename))





def main():
    print(sys.argv)
    os.environ['RUN_ID']=sys.argv[1]
    init_dir()
    index=generate_all_index("/rt-thread/sdk-index/index.json")
    #check schema
    index_schema_check(index)
    #pr this Index
    changed_pkgs =pr_index(index)
    removes=changed_pkgs["del"]
    adds=changed_pkgs["add"]
    if len(removes)==0:
        if len(adds)==0:
            logging.info("no pkg changed")
            sys.exit(0)
        else:
            logging.info("download changed pkgs...")
            logging.info("start check...")
            #check the pkg
            check_pkgs()
    else:
        logging.info("Please do not delete the old release if it`s still necessary,contact the repository admin to merge: "+str(removes))
        sys.exit(1)
    
if __name__ == "__main__":
    main()
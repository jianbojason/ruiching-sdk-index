#!/usr/bin/env python3
# coding=utf-8
import sys
import time
import urllib.request
import json
import logging
import traceback
import codecs
import os
# import mail_send

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class PackagesSync:


    def gogs_create_organization(self, org):
        GOGS_URL   = os.environ["GOGS_URL"]
        GOGS_TOKEN = os.environ["GOGS_TOKEN"]
        # GOGS_URL   = 'https://api.rt-thread.com/gogs'
        # GOGS_TOKEN =  '56c5f9a539e7390913e74c959a033c4d1584116a'

        url = '%s/api/v1/admin/users/root/orgs?token=%s'
        url = url % (GOGS_URL, GOGS_TOKEN)
        #print('url: '+url)
        data = '{"username": "%s"}'
        data = data % (org)
        data = data.encode('utf-8')
        headers = {"Content-type": "application/json"}
        request = urllib.request.Request(url, headers=headers, data=data)
        # request = urllib.request.Request(url, data, {'content-type': 'application/json'})
        try:
            response = urllib.request.urlopen(request) 
            resp = response.read().decode('utf-8')
        # except urllib.URLError,e:
        except Exception as e:
            logging.error('create organization: '+org+' failed')
            logging.error("Error message: {0}.".format(e))
            # print('e.code  : '+str(e.code) )
            # print('e.reason: '+str(e.reason) )
            resp = '{"id":0}'
        logging.error('create organization: '+org)
        #print(resp)
        return json.loads(resp)

    def gogs_get_or_create_organization(self, org):
        GOGS_URL   = os.environ["GOGS_URL"]
        GOGS_TOKEN = os.environ["GOGS_TOKEN"]
        # GOGS_URL   = 'https://api.rt-thread.com/gogs'
        # GOGS_TOKEN =  '56c5f9a539e7390913e74c959a033c4d1584116a'

        url = '%s/api/v1/orgs/%s?token=%s'
        url = url % (GOGS_URL, org, GOGS_TOKEN)
        # logging.error('gogs_get_or_create_organization url: '+url)
        request = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(request)
            resp = response.read().decode('utf-8')
        except Exception as e:
            if not hasattr(e, 'code'):
                logging.error('Get organization: '+org+' failed, and no http code!')
                logging.error("Error message: {0}.".format(e))
                return
            elif e.code == 404:
                return self.gogs_create_organization(org)
            elif e.code == 410:
                return self.gogs_create_organization(org)
        #logging.error(resp)
        return json.loads(resp)


    # POST /repos/migrate
    def gogs_migrate_repositories(self, org, repo, org_info):
        GOGS_URL   = os.environ["GOGS_URL"]
        GOGS_TOKEN = os.environ["GOGS_TOKEN"]
        GITHUB_PROXY_URL = os.environ["GITHUB_PROXY_URL"]

        # GOGS_URL   = 'https://api.rt-thread.com/gogs'
        # GOGS_TOKEN =  '56c5f9a539e7390913e74c959a033c4d1584116a'
        # GITHUB_PROXY_URL = 'https://github-proxy.rt-thread.io'

        url = '%s/api/v1/repos/migrate?token=%s'
        url = url % (GOGS_URL, GOGS_TOKEN)
        #print('Migrate Repositories url: '+url)
        clone_addr = 'https://github.com/%s/%s.git'
        data = {}
        data['clone_addr'] = '%s/%s/%s.git' % (GITHUB_PROXY_URL, org, repo) # 这里指定镜像地址
        data['mirror'] = True # 说明这是一个镜像仓库
        data['uid'] = org_info['id']
        data['repo_name'] = repo
        data = json.dumps(data)
        data = data.encode('utf-8')
        #print('data: '+data)
        request = urllib.request.Request(url, data, {'content-type': 'application/json'})
        try:
            response = urllib.request.urlopen(request)
            resp = response.read().decode('utf-8')
        except Exception as e:
            logging.error('Migrate Repositories: '+org+'/'+repo+' failed')
            logging.error("Error message: {0}.".format(e))
            # print('e.code  : '+str(e.code) )
            # print('e.reason: '+str(e.reason) )
        logging.error('Migrate ' + org + ' ' + repo)
        #print(resp)

    #http://abc.com/api/v1/orgs/group_root_test/repos?token=token
    def gogs_get_or_create_Repositories(self, org, repo, org_info):
        GOGS_URL   = os.environ["GOGS_URL"]
        GOGS_TOKEN = os.environ["GOGS_TOKEN"]
        # GOGS_URL   = 'https://api.rt-thread.com/gogs'
        # GOGS_TOKEN =  '56c5f9a539e7390913e74c959a033c4d1584116a'
        url = '%s/api/v1/orgs/%s/repos?token=%s'
        url = url % (GOGS_URL, org, GOGS_TOKEN)
        
        # 初始化resp变量
        resp = '[]'  # 默认空数组JSON字符串
        
        try:
            response = urllib.request.urlopen(request)
            resp = response.read().decode('utf-8')
        except Exception as e:
            logging.error('Get: '+org+ ' Repositories: '+repo+' failed')
            logging.error("Error message: {0}.".format(e))
            # print('e.code  : '+str(e.code) )
            # print('e.reason: '+str(e.reason) )
        print(resp)
        org_repos_json = json.loads(resp)
        print(org_repos_json)
        for item in org_repos_json:
            if item['name'] == repo:
                print(item['name'] + ' Already existed, sync...')
                url = '%s/api/v1/repos/%s/%s/mirror-sync?token=%s' # /repos/:owner/:repo/mirror-sync
                url = url % (GOGS_URL, org, repo, GOGS_TOKEN)
                request = urllib.request.Request(url, data=''.encode('utf-8'), headers={'content-type': 'application/json'})
                try:
                    response = urllib.request.urlopen(request)
                    resp = response.read().decode('utf-8')
                except Exception as e:
                    logging.error('Get: '+org+ ' Repositories: '+repo+' failed')
                    logging.error("Error message: {0}.".format(e))
                    # print('e.code  : '+str(e.code) )
                    # print('e.reason: '+str(e.reason) )
                return
        self.gogs_migrate_repositories(org, repo, org_info)

    def create_repo_in_gogs(self, org, repo_name):
        #logging.INFO('create_repo_in_gogs, org=[%s], repo_name=[%s]'%(org, repo_name))
        org_info = self.gogs_get_or_create_organization(org)
        self.gogs_get_or_create_Repositories(org, repo_name, org_info)

    def fetch_packages_info_from_git(self, bsp_git_path):
        logging.info('======>Fetch package info from git repo: ' + bsp_git_path)
        tmp = bsp_git_path.split('/')

        org = tmp[3]  # 获取 'RT-Thread-Studio'
        repo = tmp[4]  # 获取 'sdk-bsp-rk3506-realthread-ruichingpi.git'
        repo_name = repo.replace('.git', '')  # 去除.git后缀得到 'sdk-bsp-rk3506-realthread-ruichingpi'

        self.create_repo_in_gogs(org, repo_name)


def get_gogs_access_token():
    try:
        # return "56c5f9a539e7390913e74c959a033c4d1584116a"
        return os.environ["GOGS_TOKEN"]
    except Exception as e:
        logging.error("Error message: {0}.".format(e))
        traceback.print_exc()
        print('get access token fail')


def init_logger():
    log_format = "%(module)s %(lineno)d %(levelname)s %(message)s \n"
    date_format = '%Y-%m-%d  %H:%M:%S %a '
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        datefmt=date_format,
                        )

repo_url = 'https://github.com/RT-Thread-Studio/sdk-bsp-rk3506-realthread-ruichingpi.git' 
def main():
    init_logger()

    try:
        logging.info("Begin to sync ruiching bsp packages")

        time_start = time.time()
        logging.info('Synchronization script start time : %s' %
              time.asctime(time.localtime(time.time())))

        # get access token from server
        token = get_gogs_access_token()
        logging.debug("access token  : %s" % token)

        packages_updata = PackagesSync()

        packages_updata.fetch_packages_info_from_git(repo_url)

        # 显示程序运行时间
        time_end = time.time()

        logging.info('Synchronization script end time : %s' %
              time.asctime(time.localtime(time.time())))
        logging.info('Time cost : %s' % str(time_end - time_start))

        sys.exit(0)

    except Exception as e:
        # mail_send.send_email_2_revcer("zhangyuan@rt-thread.com", "[Notice ERROR] " + str(e))
        logging.error("Error message: {0}.".format(e))
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

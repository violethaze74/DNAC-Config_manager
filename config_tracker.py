import requests
import utils
import time
import logging
import dnac_apis
import os
from requests.auth import HTTPBasicAuth  # for Basic Auth
from config import DNAC_URL, DNAC_PASS, DNAC_USER, roomId, bot_token
import git
from prettytable import PrettyTable
import pyCiscoSpark as teams

# init file name and directory, nothing to change here
filename = ''
path_to_file = ''

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)
pretty_device_info = PrettyTable(['Hostname', 'Family', 'Serial Number', 'Mac Address', 'Location', 'Status', 'Config'])
pretty_device_info.padding_width = 1


def main():
    get_device_config()


def get_device_config():
    """
    This function will retrieve managed device information used to grab config
    """
    print("Getting Device Config ...")
    ios_cmd = "show run"
    devices = dnac_device_info()
    for device in devices:
        print("Checking " + device['hostname'] + " Configuration")
        run_config = dnac_apis.get_output_command_runner(ios_cmd, device['hostname'], dnac_token)
        commit_device_config(device, run_config)
    print(pretty_device_info)


def commit_device_config(device, config):
    """
    Function handles config version control
    """
    global filename, path_to_file
    filename = str(device['hostname']) + '_run_config.txt'
    path_to_file = "./device_config/" + str(device['family'] + "/" + str(device['hostname']))
    if not os.path.exists(path_to_file):
        os.makedirs(path_to_file)
    with open(os.path.join(path_to_file, filename), 'w') as f_temp:
        f_temp.write("New Config - 9")
        f_temp.write(config)
        f_temp.seek(0)  # reset the file pointer to 0
        f_temp.close()
        handle_git(device)


def handle_git(device):
    """
    Function handles config version control
    """
    try:  # Check if the dir is a repo
        repo = git.Repo(path_to_file).git_dir
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.init(path_to_file)
    try:  # commit changes and output the Diff
        repo = git.Repo(path_to_file)
        repo.git.add(filename)
        repo.git.commit(m=str(filename + ' Changed'))
        check_diff()
        pretty_device_info = pretty_print(device, "Configuration change detected")
    except Exception:
        pretty_device_info = pretty_print(device, "No Configuration change detected")


def check_diff():
    """
    Function checks the diff between base config and latest config changes
    """
    print(path_to_file)
    print(filename)
    repo = git.Repo.init(path_to_file)
    commits = list(repo.iter_commits('--all', paths=filename))
    # for commit in commits:
    #     print("Committed by %s on %s with sha %s" % (
    #     commit.committer.name, time.strftime("%a, %d %b %Y %H:%M", time.localtime(commit.committed_date)),
    #     commit.hexsha))
    diff = repo.git.diff(commits[-1], commits[0])
    post_msg(diff)
    print(diff)
    print("\n")


def pretty_print(device, config_status):
    """
    Function prints to command line nicely
    """
    pretty_device_info.add_row([device['hostname'], device['family'], device['serialNumber'], device['macAddress'],
                         device['location'],
                         device['reachabilityStatus'],
                         config_status])
    return pretty_device_info


def dnac_device_info():
    """
    Collect Managed Device information from Cisco DNA Center
    """
    all_devices_info = dnac_apis.get_all_device_info(dnac_token)
    filtered_device_list = []
    for device in all_devices_info:
        if device['family'] == 'Switches and Hubs' or device['family'] == 'Routers' or device['family'] == 'Wireless Controller':
            device_info = {}
            devices_local = dnac_apis.get_device_location(device['hostname'], dnac_token)
            device_info['id'] = device['id']
            device_info['reachabilityStatus'] = device['reachabilityStatus']
            device_info['serialNumber'] = device['serialNumber']
            device_info['family'] = device['family']
            device_info['hostname'] = device['hostname']
            device_info['macAddress'] = device['macAddress']
            device_info['location'] = devices_local
            filtered_device_list.append(device_info)
    return filtered_device_list


def post_msg(diff_data):
    """
    Post Diff found in run config to Webex Teams
    """
    print("Posting msgs")
    md = "**Base Configuration Change Detected** \n"
    teams.post_markdown(bot_token, roomId, md)
    teams.post_message(bot_token,roomId, diff_data)


if __name__ == '__main__':
    print("GET Cisco DNA Center Token...")
    # logging information here
    logging.basicConfig(
        filename='application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    dnac_token = dnac_apis.get_dnac_jwt_token(DNAC_AUTH) # DNAC API Token
    main()
from requests.api import head
import yaml
import sys
import getopt
import requests
from github import Github, GithubException, Repository
import io
import pprint
import json

def updateRepoFile(gitObject, token):
    """
    This function allows to update the settings.yaml file.
    All the repos that can be accessed by the user with the 
    token will be recorded in the settings.yaml file.
    
    Arguments:
    gitObject   - Object created from the token
    token       - token of the user
    """
    try:
        print("[INFO] reading all repos...")
        repos = gitObject.get_user().get_repos()
        print("[SUCCESS] done reading all repos...")
        repoDict = {}
        print("[INFO] mapping all branches...")
        for repo in repos:
            repoDict['token'] = token
            repoDict[repo.name] = {}
            repoURL = repo.url.replace("api.", "")
            repoURL = repoURL.replace("repos/", "")
            repoURL += ".git"
            repoDict[repo.name]['url'] = repoURL
            
            branches = list(repo.get_branches())
            branchList = []
            for branch in branches:
                branchList.append(branch.name)
            
            repoDict[repo.name]['branches'] = branchList
        print("[SUCCESS] done mapping all branches...")

        print("[INFO] updating settings.yaml file...")
        with io.open('settings.yaml', 'w', encoding='utf8') as outfile:
            yaml.safe_dump(repoDict, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False, line_break='\n')
        
        return True
    except Exception as e:
        print("[ERROR]", e.__class__, "exception thrown")
        print("Please retry!!!")
        return False


def updateWithLink(link, token):
    """
    This function allows to update the settings.yaml file.
    When a link of an organization is passed as an argument, the function will
    get all the public repos belong to that organization and record them in the
    settings.yaml file.
    
    Arguments:
    link   - Git link of the organization
    token  - token of the user

    Returns: boolean
    """
    try:
        repoDict = {}
        with open("settings.yaml", 'r') as stream:
            repoDict = yaml.safe_load(stream)

        print("[INFO] reading all repos...")
        headers = {'Authorization': 'token %s' % token}

        url = link.replace("github.com", "api.github.com/orgs")
        url += "/repos"
        res = requests.get(url, headers=headers).json()
        print("[SUCCESS] done reading all repos...")

        print("[INFO] mapping all branches...")
        for repo in res:
            repoDict[repo["name"]] = {}
            repoDict[repo["name"]]['url'] = repo["html_url"] + ".git"
            
            branches_url = repo["branches_url"].replace("{/branch}", "")
            branch_res = requests.get(branches_url, headers=headers).json()
            branchList = []
            for branch in branch_res:
                branchList.append(branch["name"])

            repoDict[repo["name"]]['branches'] = branchList

        print("[SUCCESS] done mapping all branches...")

        print("[INFO] updating settings.yaml file...")
        with io.open('settings.yaml', 'w', encoding='utf8') as outfile:
            yaml.safe_dump(repoDict, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False, line_break='\n')
        
        return True

    except Exception as e:
        print("[ERROR]", e.__class__, "exception thrown")
        print("Please retry!!!")
        return False


def createNewBranch(git, reponame, source, target):
    """
    This function will create a new branch from the source branch 
    in the same repository.
    
    Arguments:
    git     - git object
    reponame- name of the repository
    source  - source branch
    target  - target branch

    Returns: boolean
    """
    try:
        repo = git.get_user().get_repo(reponame)
        sourceBranch = repo.get_branch(source)
        repo.create_git_ref(ref="refs/heads/" + target, sha=sourceBranch.commit.sha)

        status = repo.get_branch(target)
        
        # if the branch is created, name of the returned branch object will be same as target
        # this is used for error checking
        if status.name == target:
            return True
        else:
            return False
    except GithubException as e:
        print("\n[ERROR] Exception Thrown | ", e.data["message"])
        return False


def verifyData(reponame, source):
    """
    This function will verify if the given repository and source branch is
    existing in the local settings.yaml file.

    Arguments:
    reponame    - name of the repository
    source      - source branch

    Returns: boolean
    """
    data_loaded = {}
    with open("settings.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    if reponame in data_loaded:
        if source in data_loaded[reponame]['branches']:
            return True
        else:
            return False
    else:
        return False


def getAccessToken():
    """
    This function will get the access token from the settings file and return it.

    Returns: string
    """
    with open("settings.yaml", 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    return data_loaded['token']


def printHelp():
    """
    This function prints help information
    """
    print("[INFO] Usage -- python git_interface.py <arguments>")
    print("\n[INFO] Possible Arguments -- ")
    print("\t-s <source branch>\n\t-t <target branch>\n\t-r <repository>\n\t-u <to update settings from user (no additional arguments needed)>\n\t-l <link of the organizations to update settings (optional)>")
                    


def main(argv):
    source = ''
    target = ''
    repoName = ''

    # get the arguments from the user
    try:
        opts, args = getopt.getopt(argv, "hul:s:t:r:", ["link=", "src=", "trg=", "repo="])
        
        # checks if required arguments are inserted
        if len(opts) > 0:
            for opt, arg in opts:
                # helper argument
                if opt == '-h':
                    printHelp()
                    sys.exit()

                # update option with user
                elif opt == "-u":
                    print("\n[INFO] Logging in using token...")
                    token = getAccessToken()
                    gitObject = Github(token)
                    print("[INFO] Successfully logged in...")

                    status = updateRepoFile(gitObject, token)
                    if status == False:
                        sys.exit(3)
                    if status == True:
                        print("[SUCCESS] settings.yaml file updated successfully...")  

                # update option with link
                elif opt in ("-l", "--link"):
                    print("\n[INFO] Logging in using token...")
                    token = getAccessToken()
                    print("[INFO] Successfully logged in...")

                    link = arg
                    status = updateWithLink(link, token)
                    if status == False:
                        sys.exit(3)
                    if status == True:
                        print("[SUCCESS] settings.yaml file updated successfully...") 

                # source branch
                elif opt in ("-s", "--src"):
                    source = arg

                # target branch
                elif opt in ("-t", "--trg"):
                    target = arg  
                
                # repository name
                elif opt in ("-r", "--repo"):
                    repoName = arg 

            # if source, target and repo all three are not empty
            if source != '' and target != '' and repoName != '':
                # create an git object using the access token of the user
                print("\n[INFO] Logging in using token...")
                token = getAccessToken()
                gitObject = Github(token)
                print("[INFO] Successfully logged in...")

                # verify the repo name and source from the local settings
                print("\n[INFO] verifying availability of the repo and branch...")
                status = verifyData(repoName, source)
                if status == False:
                    print("\n[ERROR] repo and/or branch not available in settings file\n[SOLUTION] try updating the settings file")
                else:
                    # if both available create the new branch
                    print("[SUCCESS] repo and branch available...")
                    status = createNewBranch(git = gitObject, reponame = repoName, source = source, target = target)
                    if status == False:
                        print("[ERROR] Repo creation failed.")
                    else:
                        print("\n[SUCCESS] Repo/branch created.")
            else:
                print("\n[INFO] Program will exit now.")
        else:
            printHelp()
            sys.exit()

    except getopt.GetoptError:
       printHelp()
       sys.exit(1)
    
    


if __name__ == '__main__':
    main(sys.argv[1:])

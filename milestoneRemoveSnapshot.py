""" Script to do milestone release.
    Usage: python milestoneRemoveSnapshot.py <user-id>"""

import subprocess
import os
import sys
import shlex
from xml.etree import ElementTree
import shutil
import json

#VARIABLES
TEMP_FOLDER_NAME = "Milestone_Release_Folder"
HONENAME = 'git.wdf.sap.corp'
PORT = '29418'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


REVIEWERS = ['prem.roshan.madhusudhan.nair@sap.com','ananya.mallik@sap.com','girish.sainath@sap.com','sarath.gopal@sap.com','shwetha.kalyanathaya.shashidhara@sap.com']

#UTILITY FUNCTIONS
def change_parent_pom(filename):
    #creating ElementTree for the POM file.
    ElementTree.register_namespace('',"http://maven.apache.org/POM/4.0.0")
    TREE = ElementTree.parse(filename)
    ROOT = TREE.getroot()
    VERSION = ROOT.findall('*')[3]
    if "SNAPSHOT" in VERSION.text:
        VERSION.text = VERSION.text.split('-')[0]
    else:
        return -1
    TREE.write('pom.xml')
    return 1

def change_nonparent_pom(filename):
    #creating ElementTree for the POM file.
    ElementTree.register_namespace('',"http://maven.apache.org/POM/4.0.0")
    TREE = ElementTree.parse(filename)
    ROOT = TREE.getroot()
    VERSION = ROOT.findall('*')[1].findall('*')[3]
    if "SNAPSHOT" in VERSION.text:
        VERSION.text = VERSION.text.split('-')[0]
    else:
        return -1
    TREE.write('pom.xml')
    return 1

def run_command(command):
    print("Executing command : %s" % (command))
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    (out, err) = process.communicate()

def formReviewerString():
    """Returns the reviewer string for gerrit review"""
    result = ""
    for reviewer in REVIEWERS:
        if result == "":
            result = result + "r="+reviewer
        else:
            result = result + ",r=" + reviewer
    return result

def main(USERID):
    #Read json file containing projects information
    with open('Projects.json','r') as f:
        projects = json.load(f)

    #creating a separate directory.
        os.mkdir(TEMP_FOLDER_NAME)
        os.chdir(TEMP_FOLDER_NAME)

    #MAIN
    for project in projects:
        #cloning master branch
        CLONECOMMAND = "git clone -b master ssh://"+USERID+"@git.wdf.sap.corp:29418"+project["git"]
        run_command(CLONECOMMAND)
        os.chdir(project["projectfolder"])

        #copying commit msg hook file for commit to be possible
        shutil.copy2(DIR_PATH + "\\commit-msg", ".\\.git\\hooks")

        if project.get("hasparent") is None :
            if change_parent_pom("pom.xml") == -1:
                print("********* ERROR *************\nProject %s failed. POM did not contain snapshot." % (project['name']))
                continue
        else :
            #changing parent folder pom
            if change_parent_pom(project["parentfolder"]+"\\pom.xml") == -1:
                print("********* ERROR *************\nProject %s failed. POM for folder %s did not contain snapshot." % (project['name'], project['parentfolder']))
                continue
            
            #changing for all subfolder poms
            for subproject in project["subprojects"]:
                if change_parent_pom(project["parentfolder"]+"\\pom.xml") == -1:
                    print("********* ERROR *************\nProject %s failed. POM for folder %s did not contain snapshot." % (project['name'], subproject['folder']))
                    continue

        #pushing the change to gerrit
        run_command("git add .")
        run_command("git commit -m 'MilestoneRelease "+project['name']+"'")
        pushcommand = "git push ssh://"+USERID+"@"+HONENAME+":"+PORT+project["git"] + " HEAD:refs/for/master%"+formReviewerString()
        # run_command(pushcommand)
        os.chdir(DIR_PATH + "\\" + TEMP_FOLDER_NAME)

if __name__ == '__main__':
    USERID = sys.argv[1]
    main(USERID)

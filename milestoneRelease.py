""" Script to do milestone release.
    Usage: python milestoneRelease.py <project-name> <old-project-version> <new-project-version>"""

import subprocess
import os
import sys
import shlex
from xml.etree import ElementTree
import shutil

#VARIABLES
USERID = sys.argv[1]
TEMP_FOLDER_NAME = "Milestone_Release_Folder"
HONENAME = 'git.wdf.sap.corp'
PORT = '29418'
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

#DICTIONARY TO STORE PROJECTS NAME
PROJECTS = {}
PROJECT_FOLDER_NAMES = {}
PROJECTS['designtime'] = '/fnf/Do/sap.smbaas.ui.designtime.git'
PROJECTS['runtime'] = '/fnf/Do/sap.smbaas.ui.runtime.git'
PROJECT_FOLDER_NAMES['designtime'] = 'sap.smbaas.ui.designtime'
PROJECT_FOLDER_NAMES['runtime'] = 'sap.smbaas.ui.runtime'
REVIEWERS=['raghavendran.radhakrishnan@sap.com', 'kartik.s.gayatri@sap.com']

#UTILITY FUNCTIONS
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


#MAIN
for key, value in PROJECTS.items():
    #creating a separate directory.
    os.mkdir(TEMP_FOLDER_NAME)
    os.chdir(TEMP_FOLDER_NAME)

    #cloning master branch
    CLONECOMMAND = "git clone -b master ssh://"+USERID+"@git.wdf.sap.corp:29418"+PROJECTS[key]
    run_command(CLONECOMMAND)
    os.chdir(PROJECT_FOLDER_NAMES[key])

    #copying commit msg hook file for commit to be possible
    shutil.copy2(DIR_PATH + "\\commit-msg", ".\\.git\\hooks")
 
    #creating ElementTree for the POM file.
    ElementTree.register_namespace('',"http://maven.apache.org/POM/4.0.0")
    TREE = ElementTree.parse("pom.xml")
    ROOT = TREE.getroot()
    VERSION = ROOT.findall('*')[3]
    if "SNAPSHOT" in VERSION.text:
        VERSION.text = VERSION.text.split('-')[0]
    else:
        print("********* ERROR *************\nProject %s failed. POM did not contain snapshot." % (PROJECTS[key]))
        continue
    TREE.write('pom.xml')

    #pushing the change to gerrit
    run_command("git add .")
    run_command("git commit -m 'MilestoneRelease"+key+"'")
    pushcommand = "git push ssh://"+USERID+"@"+HONENAME+":"+PORT+PROJECTS[key] + " HEAD:refs/for/master%"+formReviewerString()
    run_command(pushcommand)


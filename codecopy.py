""" Generic Script to perfrom code copy from one branch to another
    Usage: python codecopy.py <srcBranch> <targetBranch> <userid> <!optional:project>"""

import subprocess
import sys
import os
import shlex
import shutil
from filereplace import replaceDirectoryFiles

#setting variables
tempFolderName = 'Code_Copy_Temp_Folder'
dir_path = os.path.dirname(os.path.realpath(__file__))
hostName = 'git.wdf.sap.corp'
port = '29418'
designtime = '/fnf/Do/sap.smbaas.ui.designtime.git'
designtimeFolderName = 'sap.smbaas.ui.designtime'
srcBranch = str(sys.argv[1])
targetBranch = str(sys.argv[2])
userid = str(sys.argv[3])
if len(sys.argv) > 4:
    project = str(sys.argv[4])
else :
    project = ""
reviewers=['prem.roshan.madhusudhan.nair@sap.com','ananya.mallik@sap.com','girish.sainath@sap.com','sarath.gopal@sap.com','shwetha.kalyanathaya.shashidhara@sap.com']

#DICTIONARY TO STORE PROJECTS NAME
PROJECTS = {}
PROJECT_FOLDER_NAMES = {}
FOLDER_TO_COPY = {}
PROJECTS['designtime'] = '/fnf/Do/sap.smbaas.ui.designtime.git'
PROJECTS['runtime'] = '/fnf/Do/sap.smbaas.ui.runtime.git'
PROJECTS['javacore'] = '/sap.smartbusiness.service.core.git'
PROJECTS['javaclassic'] = '/sap.smartbusiness.service.hcp.classic.git'
PROJECTS['javacf'] = '/sap.smartbusiness.service.cf'
PROJECTS['contentstorecore'] = '/sap.smartbusiness.content.store.core.git'
PROJECTS['contentstoreclassic'] = '/sap.smartbusiness.content.store.hcp.classic.git'
PROJECTS['contentstorecf'] = '/sap.smartbusiness.content.store.hcp.cf.git'

PROJECT_FOLDER_NAMES['designtime'] = 'sap.smbaas.ui.designtime'
PROJECT_FOLDER_NAMES['runtime'] = 'sap.smbaas.ui.runtime'
PROJECT_FOLDER_NAMES['javacore'] = 'sap.smartbusiness.service.core'
PROJECT_FOLDER_NAMES['javaclassic'] = 'sap.smartbusiness.service.hcp.classic'
PROJECT_FOLDER_NAMES['javacf'] = 'sap.smartbusiness.service.cf'
PROJECT_FOLDER_NAMES['contentstorecore'] = 'sap.smartbusiness.content.store.core'
PROJECT_FOLDER_NAMES['contentstoreclassic'] = 'sap.smartbusiness.content.store.hcp.classic'
PROJECT_FOLDER_NAMES['contentstorecf'] = 'sap.smartbusiness.content.store.hcp.cf'

FOLDER_TO_COPY['designtime'] = "\\src\\main\\webapp"
FOLDER_TO_COPY['runtime'] = "\\webapp"
FOLDER_TO_COPY['javacore'] = "\\sap-smartbusiness-service-core\\src\\main"
FOLDER_TO_COPY['javaclassic'] = "\\sap-smartbusiness-service-hcp-classic\\src\\main"
FOLDER_TO_COPY['javacf'] = "\\java\\src\\main"
FOLDER_TO_COPY['contentstorecore'] = "\\sap-smartbusiness-content-store-core\\src\\main"
FOLDER_TO_COPY['contentstoreclassic'] = "\\sap-smartbusiness-content-store-hcp-classic\\src\\main"
FOLDER_TO_COPY['contentstorecf'] = "\\src\\main"

def run_command(command):
    print("Executing command : %s" % (command))
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    (out, err) = process.communicate()

def formReviewerString():
    """Returns the reviewer string for gerrit review"""
    result = ""
    for reviewer in reviewers:
        if result == "":
            result = result + "r="+reviewer
        else:
            result = result + ",r=" + reviewer
    return result

# removing the projects that are not selected by user
TEMP_PROJECTS = PROJECTS
if project != "":
    for key,value in list(TEMP_PROJECTS.items()):
        if project == key:
            continue
        del PROJECTS[key]


#creating temporary directory to hold cloned folders
os.mkdir(tempFolderName)
os.chdir(tempFolderName)

#creating separate directories for cloning gits
os.mkdir(srcBranch)
os.mkdir(targetBranch)

for key, value in PROJECTS.items():
    # cloning src branch
    os.chdir(srcBranch)
    clonecommand = "git clone -b " + srcBranch +" ssh://"+userid+"@git.wdf.sap.corp:29418"+PROJECTS[key]
    run_command(clonecommand)
    os.chdir("..")

    #cloning target branch
    os.chdir(targetBranch)
    clonecommand = "git clone -b " + targetBranch +" ssh://"+userid+"@git.wdf.sap.corp:29418"+PROJECTS[key]
    run_command(clonecommand)
    os.chdir("..")

    #setup(Copying commit-msg hook into git folders for getting change id in commit message)
    shutil.copy2("..\\commit-msg",srcBranch+"\\"+PROJECT_FOLDER_NAMES[key]+"\\.git\\hooks")
    shutil.copy2("..\\commit-msg",targetBranch+"\\"+PROJECT_FOLDER_NAMES[key]+"\\.git\\hooks")

    #replacing webapp folder in target folder with webapp folder in src folder
    relativePath = "\\"+ PROJECT_FOLDER_NAMES[key] +FOLDER_TO_COPY[key]
    srcFolderPath =  dir_path+"\\"+tempFolderName+"\\"+srcBranch + relativePath
    targetFolderPath =  dir_path + "\\"+ tempFolderName+"\\"+ targetBranch + relativePath
    print ("Target Folder: " + targetFolderPath)
    replaceDirectoryFiles(srcFolderPath,targetFolderPath)


    #committing the changes and pushing the changes to gerrit
    os.chdir(targetBranch+"\\"+PROJECT_FOLDER_NAMES[key])
    run_command("git add .")
    run_command("git commit -m 'CodeCopy'")
    pushcommand = "git push ssh://"+userid+"@"+hostName+":"+port+PROJECTS[key] + " HEAD:refs/for/"+targetBranch+"%"+formReviewerString()
    run_command(pushcommand)

    os.chdir(dir_path+"\\"+tempFolderName)

print("CODE COPY SUCCESSFUL")
print("Removing Temp Files Created")

os.chdir(dir_path)
print(os.getcwd())
#shutil.rmtree(dir_path+"\\"+tempFolderName,ignore_errors=True)
#os.removedirs(tempFolderName)
# print ("Script executed successfully")